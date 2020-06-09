#!/usr/bin/python

import math
from math import log
from nltk import word_tokenize

word_d = {}
sent_list = []

def process_new_sentence(s):
	sent_list.append(s)
	tokenized = word_tokenize(s)
	for word in tokenized:
		if word not in word_d.keys():
			word_d[word]=0
		word_d[word] += 1

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
	count=0
	for t in bow:
		
		cnt = 0
		for s in sent_list:
			#count=count+1
			#print(count)
			if t in word_tokenize(s):
				
				cnt += 1
			
		idf_d[t]=log(Dval/cnt)
	#print("ok!!!!!!")
	return idf_d

def tf_idf(s, n):
	
	
	for i in range(len(s)):
		process_new_sentence(s[i])
	
	idf_d = compute_idf()
	
	tf_d = compute_tf(sent_list[n])
	result ={}
		
	for word,tfval in tf_d.items():
		result[word]=tfval*idf_d[word]
	result2 = sorted(result.items(), key=lambda x: x[1], reverse=True)

	ret=[]
	ret2=[]
	for i in range(0, 10):
		if i>len(result2)-1:
			break;
		ret.append(result2[i][0])
		print("%-6s %6f" %(result2[i][0], result2[i][1]))
	
		
	print(" ")
	return ret
