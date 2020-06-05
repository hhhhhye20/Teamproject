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
def home(URL=None):
    return render_template('home.html', URL=URL)

@app.route('/home/textInput', methods=['POST'])
def search_url():

    if request.method == 'POST':
        url = request.form['URL']
    
    res = requests.get(url)

    html = BeautifulSoup(res.content, "html.parser")

    return html.text



def allowed_file(filename):
    return '.' in filename and \
            filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/home/fileUpload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)

        f = request.files['file']

        if f.filename == '':
            return redirect(request.url)

        if f and allowed_file(f.filename):
            filename = secure_filename(f.filename)
            f.save(filename)
            
            f = open(filename, 'r')
            
            htmlList = []
            while True:
                url = f.readline().strip()
                
                if not url:
                    break

                res = requests.get(url)

                html = BeautifulSoup(res.content, "html.parser")
                        
                htmlList.append(html.text)
        

    return render_template('home.html', urlList=htmlList)

if __name__ == '__main__':
    app.run(debug = True)
