#!/usr/bin/python
import re 
import requests 
from bs4 import BeautifulSoup 
from flask import Flask, render_template, request

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
				res = requests.get(url) 
				html = BeautifulSoup(res.content, "html.parser") 
				html = html.find_all(class_='Box-row')
				a=[]

				for alist in html:
					lists = alist.find(class_='h3 lh-condensed').text
					a.append(lists)
	

				str1='/'.join(a)
				strList=str1.split('/')
		
				for i in range(len(strList)):
					strList[i]=strList[i].strip()
	
				result=[]
				result2=[]
				for i in range(1,len(strList),2):
					print(strList[i])
					result.append(strList[i])
				for i in range(0,len(strList),2):
					print(strList[i])
					result2.append(strList[i])
			

		return 'upoads directory!'

if __name__ == '__main__':
	app.run(debug = True)
