#!/usr/bin/python
import re 
import requests 
from bs4 import BeautifulSoup 
from flask import Flask, render_template, request
from urllib.request import urlopen
import tf
import content_management 
import Content

app = Flask(__name__)

@app.route('/')
def render_file():
	return render_template("upload.html")

@app.route('/fileUpload', methods=['GET', 'POST'])

def upload_file():
	flash("asd")
	if request.method == 'POST':
		f=request.files['file']
		f.save(f.filename)
		result=[]
		with open(f.filename,"r") as f:
			for line in f:
				url=line
				html = urlopen(url).read() 
				html = BeautifulSoup(html, "html.parser") 
				
				html = html.find_all('p')
				a=[]

				for alist in html:
					lists = alist.text
					a.append(lists)
	

				str1='/'.join(a)
				dlist = [",", ".", "'", ";", "!", "\n", "©", "»", "(", ")"]
				for c in dlist:
					str1=str1.replace(c, " ")
				strList=str1.split('/')
				

				for i in range(len(strList)):
					strList[i]=strList[i].strip()
				
				strList=' '.join(strList)
				result.append(strList)
		tftest=tf.tf_idf(result, 0)
		return render_template("world_analysis.html", parsed_page=tftest)

#@app.route('/tf')
#def tf_idf():
#	if request.method == 'POST':
#		f=request
#	return render_template"home.html", parsed_page=tf.tf_idf(

if __name__ == '__main__':
	
	app.run(debug = True)
	
