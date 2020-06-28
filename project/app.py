#!/usr/bin/python
#-*- coding: utf-8 -*-

import os, re, requests, math, timeit
from math import log
from nltk import word_tokenize
from bs4 import BeautifulSoup
from flask import Flask, flash, request, url_for, render_template
from werkzeug.utils import secure_filename
from elasticsearch import Elasticsearch
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel

ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

es_host="127.0.0.1" 
es_port="9200"

app = Flask(__name__)

@app.route('/')
def home(ERROR=None, numbers=0):
    
    make_index('analysis')

    return render_template('home.html', ERROR=ERROR, urlList=urlList, countList=countList, time=time, numbers=numbers)

urlList = []
textList = []
countList = []
time = []
numbers = 0

#input text
@app.route('/home/textInput', methods=['POST'])
def request_url():
    if request.method == 'POST':
            url = request.form['URL']
    if url == '':
        ERROR = "실패 : 아무것도 입력되지 않았습니다."
        return render_template('home.html', ERROR=ERROR, urlList=urlList, countList=countList, time=time, numbers=numbers ) 

    ERROR = input_items(url)
    
    tf_idf_and_cos_sim()

    return render_template('home.html', ERROR=ERROR, urlList=urlList, countList=countList, time=time, numbers=numbers ) 

def allowed_file(filename):
    return '.' in filename and \
            filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

#input file
@app.route('/home/fileUpload', methods=['GET', 'POST'])
def upload_file():
    ERROR=None

    if request.method == 'POST':
        if 'file' not in request.files:
            ERROR = "실패 : 존재하지 않는 파일입니다."
            return render_template('home.html', ERROR=ERROR, urlList=urlList, countList=countList, time=time, numbers=numbers)

        f = request.files['file']

        if f.filename == '':
            ERROR = '실패 : 파일을 정하지 않았습니다.'
            return render_template('home.html', ERROR=ERROR, urlList=urlList, countList=countList, time=time, numbers=numbers)

        if f and allowed_file(f.filename):
            filename = secure_filename(f.filename)
            f.save(filename)
            
            f = open(filename, 'r')

            while True:
                url = f.readline().strip()
                
                if not url:
                    break

                if ERROR == None:
                    ERROR = input_items(url)
                else:
                    input_items(url)

        tf_idf_and_cos_sim()

    return render_template('home.html', ERROR=ERROR, urlList=urlList, countList=countList, time=time, numbers=numbers)

#input items
def input_items(url):
                global numbers
            
                if url in urlList:
                    ERROR=" 중복 : 중복된 url을 입력하셨습니다."
                    return ERROR
                
                #processing time start
                start = timeit.default_timer()
                
                global res

                try :
                    res = requests.get(url)
                except :
                    if res.status_code == 302:
                        ERROR = "실패 : 인터넷에 연결되어 있지 않습니다."
                    else:
                        ERROR = "실패 : 부정확한 주소를 입력하셨습니다."

                    return ERROR

                html = BeautifulSoup(res.content, "html.parser")

                script_tag = html.find_all(['script', 'style', 'header', 'footer', 'form'])

                #extract 함수는 soup 객체에서 해당 태그를 제거합니다.
                for script in script_tag:
                    script.extract()
                
                # 텍스트 단위 결합을 '\n'(줄바꿈)으로 합니다.
                # 각 텍스트 단위의 시작과 끝에서 공백을 제거합니다.
                text = html.get_text('\n', strip=True)

                text = re.sub('[—·™\-=+,#/\—,/:¶>▼▲»@|→``?:^$.@*\"※~&%ㆍ!』\\‘|\(\)\[\]\<\>`\'…》]', ' ', text)
                #print(text)

                urlList.append(url)
                textList.append(text)
                countList.append(count_of_words(text))

                #processing time end
                stop = timeit.default_timer()

                time.append(round(stop - start, 2))
               
                numbers += 1

                return None


def count_of_words(s):
        tokenized = word_tokenize(s)

        return len(tokenized)


vectorizer = TfidfVectorizer() # 객체 선언

def tf_idf_and_cos_sim():
        vectorizer.fit(textList)
        words = sorted(vectorizer.vocabulary_.keys())
        tf_idf = vectorizer.transform(textList).toarray()

        cosine_matrix = vectorizer.fit_transform(textList) #벡터화
        cosine_sim = linear_kernel(cosine_matrix, cosine_matrix) #cosine 유사도

        make_index('analysis')

        for i in range(numbers):

            resultOfWord = {}
            resultOfSimilarity = {}

            for j in range(len(words)):
                resultOfWord[words[j]]=tf_idf[i][j]

            for k in range(numbers):
                resultOfSimilarity[urlList[k]]=cosine_sim[i][k]

            items = sorted(resultOfSimilarity.items(), reverse=True, key=lambda x : x[1])[1:4]
            topWords = sorted(resultOfWord.keys(), reverse=True, key=lambda x : resultOfWord[x])[0:10]
            
            urls=[]
            percents=[]

            for key, value in items:
                urls.append(key)
                percents.append(round(100*float(value), 2))

            elastic_create(topWords, urls, percents, i)


@app.route('/home/word_analysis', methods=['POST'])
def print_analysis():

    if request.method == 'POST':
        index = request.form['index']
        if numbers < 2 :
            ERROR = "실패 : 단어들의 TF_IDF를 산출해내기 위해서는 url주소가 2개 이상이어야합니다."
        else :
            ERROR = None

        return render_template('word_analysis.html', ERROR=ERROR, parsed_page=elastic_search("topWords", int(index)))


@app.route('/home/cosine_similarity', methods=['POST'])
def print_similarity():

    if request.method == 'POST':
        index = request.form['index']
        if numbers < 4 :
            ERROR = "실패 : 유사도를 분석하기 위해서는 url주소가 4개 이상이어야합니다."
        else :
            ERROR = None

        return render_template('cos_sim.html', ERROR=ERROR, top_url=elastic_search("similarities", int(index)), top_url_percent=elastic_search("Percentages", int(index)))

#elastic create
def elastic_create(topWords, similarities, percentages, number):

        e={
                "topWords": topWords,
                "similarities": similarities,
                "Percentages": percentages
        }

        res=es.index(index="analysis", doc_type='_doc',  id=number, body=e)

def elastic_search(name, number):
	res=es.get(index="analysis", doc_type="_doc", id=number)
	dic=res['_source']
	return(dic[name])

#리셋 버튼 모든 데이터를 지우고 처음 상태로 되돌아가는 버튼
@app.route('/home/reset', methods=['POST'])
def reset():
    global numbers
    ERROR = None

    if request.method == 'POST':
        reset = request.form['reset']
        if numbers < 1 :
            ERROR = "리셋 할 데이터가 없습니다."
        else :
            ERROR = "리셋을 완료하였습니다."
            make_index('analysis')
            urlList.clear()
            textList.clear()
            countList.clear()
            time.clear()
            numbers = 0

        return render_template('home.html', ERROR=ERROR, urlList=urlList, countList=countList, time=time, numbers=numbers)       


def make_index(index_name):
    """인덱스를 신규 생성한다(존재하면 삭제 후 생성) """
    if es.indices.exists(index=index_name):
        es.indices.delete(index=index_name)
    print(es.indices.create(index=index_name))

if __name__ == '__main__':
    es = Elasticsearch([{'host':es_host, 'port':es_port}], timeout=30)

    app.run(debug = True)
