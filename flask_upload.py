#!/usr/bin/python
import re 
import requests 
from bs4 import BeautifulSoup 
from flask import Flask, render_template, request
from urllib.request import urlopen

app = Flask(__name__)

@app.route('/')
def render_file():
	return render_template("upload.html")

@app.route('/fileUpload', methods=['GET', 'POST'])
def upload_file():
	if request.method == 'POST':
		f=request.files['file']
		f.save(f.filename)
		with open(f.filename,"r") as f:
			for line in f:
				url=line
				html = urlopen(url).read() 
				html = BeautifulSoup(html, "html.parser") 
				print(html)
				html = html.find_all('p')
				a=[]

				for alist in html:
					lists = alist.text
					a.append(lists)
	

				str1=' '.join(a)
				strList=str1.split(' ')
		
				for i in range(len(strList)):
					strList[i]=strList[i].strip()
	
				result=[]
			
				for i in range(0,len(strList)):
					print(strList[i])
					result.append(strList[i])
			
			

		return render_template("home.html", parsed_page=result)

if __name__ == '__main__':
	app.run(debug = True)
