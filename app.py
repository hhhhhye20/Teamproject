#!/usr/bin/python
#-*- coding: utf-8 -*-

import os
import re
import requests
from bs4 import BeautifulSoup
from flask import Flask, flash, request, redirect, url_for
from flask import render_template
from werkzeug.utils import secure_filename

ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

app = Flask(__name__)

@app.route('/')
def home(ERROR=None):
    return render_template('home.html', ERROR=ERROR)

@app.route('/home/textInput', methods=['POST'])
def search_url():

    if request.method == 'POST':
        if 'URL' not in request.files:
            return redirect(request.url)
    
    res = requests.get(url)

    html = BeautifulSoup(res.content, "html.parser")

    return 


def allowed_file(filename):
    return '.' in filename and \
            filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/home/fileUpload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return redirect(url_for('home'))

        f = request.files['file']

        if f.filename == '':
            ERROR = "파일을 정하지 않았습니다."
            return render_template('home.html', ERROR=ERROR)

        if f and allowed_file(f.filename):
            filename = secure_filename(f.filename)
            f.save(filename)
            
            f = open(filename, 'r')
            
            urlList = []
            countList = []
            time = []
            numbers = 0
            while True:
                url = f.readline().strip()
                
                if not url:
                    break

                try :
                    res = requests.get(url)
                except :

                    return redirect(url_for('home'))

                html = BeautifulSoup(res.content, "html.parser")
                        
                urlList.append(url)
                countList.append(1000)
                time.append(1)
                numbers += 1
        

    return render_template('listPrint.html', urlList=urlList, countList=countList, time=time, numbers=numbers )

if __name__ == '__main__':
    app.run(debug = True)
