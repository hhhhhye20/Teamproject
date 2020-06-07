#!/usr/bin/python
#-*- coding: utf-8 -*-

import os, re, requests, math, timeit
from math import log
from nltk import word_tokenize
from bs4 import BeautifulSoup
from flask import Flask, flash, request, redirect, url_for
from flask import render_template
from werkzeug.utils import secure_filename
from elasticsearch import Elasticsearch

ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

es_host="127.0.0.1" 
es_port="9200"
es = Elasticsearch([{'host':es_host, 'port':es_port}], timeout=30)


app = Flask(__name__)


@app.route('/')
def home(ERROR=None, numbers=0):
    return render_template('home.html', ERROR=ERROR, urlList=urlList, countList=countList, time=time, numbers=numbers)

urlList = []
textList = []
countList = []
time = []
wordList = []
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
    
    

    return render_template('home.html', ERROR=ERROR, urlList=urlList, countList=countList, time=time, numbers=numbers ) 

def allowed_file(filename):
    return '.' in filename and \
            filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

#input file
@app.route('/home/fileUpload', methods=['GET', 'POST'])
def upload_file():
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

                ERROR = input_items(url)

    #elastic search 
    es.indices.delete(index='analysis', ignore=[400,404])
    for i in range(len(urlList)):
        elastic_insert(urlList[i], countList[i], time[i], i)
        print(elastic_search("url", i))
        print(elastic_search("word_num", i))
        print(elastic_search("time", i))
    return render_template('home.html', ERROR=ERROR, urlList=urlList, countList=countList, time=time, numbers=numbers)

#input items
def input_items(url):
                global numbers
            
                if url in urlList:
                    ERROR=" 중복 : 중복된 url을 입력하셨습니다."
                    return ERROR
                
                #processing time start
                start = timeit.default_timer()

                try :
                    res = requests.get(url)
                except :
                    if res.status_code == 302:
                        ERROR = "실패 : 인터넷에 연결되어 있지 않습니다."
                    else:
                        ERROR = "실패 : 부정확한 주소를 입력하셨습니다."

                    return ERROR

                html = BeautifulSoup(res.content, "html.parser")

                #processing time end
                stop = timeit.default_timer()

                urlList.append(url)
                textList.append(html.get_text())
                countList.append(process_new_sentence(html.get_text()))
                time.append(stop - start)
                numbers += 1

                return None


word_d = {}
sent_list = []

def process_new_sentence(s):
        sent_list.append(s)
        tokenized = word_tokenize(s)

        for word in tokenized:
            if word not in word_d.keys():
                word_d[word]=0
            word_d[word] += 1
        
        return len(tokenized)
        

def compute_tf(s):
	bow = set()
	# dictionary for words in the given sentence (document)
	wordcount_d = {}

	tokenized = word_tokenize(s)
	for tok in tokenized:
		if tok not in wordcount_d.keys():
			wordcount_d[tok]=0
		wordcount_d[tok] += 1
		bow.add(tok)
	tf_d = {}
	for word,count in wordcount_d.items():
		tf_d[word]=count/float(len(bow))
	return tf_d



def compute_idf():
	Dval = len(sent_list)
	# build set of words
	bow = set()

	for i in range(0,len(sent_list)):
		tokenized = word_tokenize(sent_list[i])
		for tok in tokenized:
			bow.add(tok)

	idf_d = {}
	for t in bow:
		cnt = 0
		for s in sent_list:
			if t in word_tokenize(s):
				cnt += 1
			
		idf_d[t]=log(Dval/cnt)
	return idf_d


def tf_idf(s, n):
	for i in range(len(s)):
		process_new_sentence(s[i])
	
	idf_d = compute_idf()
	for i in range(0,len(sent_list)):
		tf_d = compute_tf(sent_list[i])
		result ={}

		for word,tfval in tf_d.items():
			result[word]=tfval*idf_d[word]
		result2 = sorted(result.items(), key=lambda x: x[1], reverse=True)

		ret={}
		ret2=[]	
		for j in range(0, 10):
			
			if j>len(result2)-1:
				break;
			#ret[result2[j][0]]=result2[j][1]
			ret2.append(result2[j][0])
			#print(type(result2[j][0]))
		
			
		if n==i:
			return ret2

@app.route('/home/word_analysis', methods=['POST'])
def print_analysis():

    if request.method == 'POST':
        index = request.form['index']
        tf_idfWordList = tf_idf(textList, int(index))
        return render_template('word_analysis.html', parsed_page=tf_idfWordList)

#elastic search
def elastic_insert(url, word_num, time, i):

	doc={'url':url, 'word_num':word_num, 'time':time}
	res=es.index(index="analysis", doc_type='word', body=doc, id=i)



def elastic_search(name, n):
	res=es.get(index="analysis", doc_type="word", id=n)
	dic=res['_source']
	return(dic[name])

def make_index(es, index_name):
    """인덱스를 신규 생성한다(존재하면 삭제 후 생성) """
    if es.indices.exists(index=index_name):
        es.indices.delete(index=index_name)
    print(es.indices.create(index=index_name))

if __name__ == '__main__':

    app.run(debug = True)
