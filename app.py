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
import tf

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
                html = html.find_all('p')

                a=[]

                for alist in html:
                        lists = alist.text
                        a.append(lists)

                str1='/'.join(a)
                dlist = [",", ".", "'", ";", "!", "\n", "©", "»", "(", ")", "$", "="]

                for c in dlist:
                        str1=str1.replace(c, " ")
                strList=str1.split('/')
                strList=str1.split(' ')
                countList.append(len(strList))
               
                for i in range(len(strList)):
                        strList[i]=strList[i].strip()
                        
                        
                strList=' '.join(strList)
               # print(strList)
               # result=[]
                #result.append(strList)

                #processing time end
                stop = timeit.default_timer()
               
                urlList.append(url)
                textList.append(strList)
                time.append(stop - start)
                
                #elastic search
                es.indices.delete(index='analysis', ignore=[400,404])
                elastic_insert(urlList[numbers], countList[numbers], time[numbers], numbers)
                print(elastic_search("url", numbers))
                print(elastic_search("word_num", numbers))
                print(elastic_search("time", numbers))

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
        

@app.route('/home/word_analysis', methods=['POST'])
def print_analysis():

    if request.method == 'POST':
        index = request.form['index']
        tf_idfWordList = tf.tf_idf(textList, int(index))
        return render_template('word_analysis.html', parsed_page=tf_idfWordList)

#elastic search
def elastic_insert(url, word_num, time, number):

	doc={'url':url, 'word_num':word_num, 'time':time}
	res=es.index(index="analysis", doc_type='word', body=doc, id=number)


def elastic_search(name, number):
	res=es.get(index="analysis", doc_type="word", id=number)
	dic=res['_source']
	return(dic[name])

def make_index(es, index_name):
    """인덱스를 신규 생성한다(존재하면 삭제 후 생성) """
    if es.indices.exists(index=index_name):
        es.indices.delete(index=index_name)
    print(es.indices.create(index=index_name))

if __name__ == '__main__':
    app.run(debug = True)
