from elasticsearch import Elasticsearch

es_host="127.0.0.1" 
es_port="9200"




def elastic_insert(data1, data2, i):
	if len(data1) != len(data2):
		print("error!")
		return
	
	doc={'TF_idf':data1, 'similarity':data2}
	res=es.index(index="analysis", doc_type='word', body=doc, id=i)
	print(res)

def elastic_search(name, n):
	res=es.get(index="analysis", doc_type="word", id=n)
	dic=res['_source']
	return(dic[name])


def make_index(es, index_name):
    """인덱스를 신규 생성한다(존재하면 삭제 후 생성) """
    if es.indices.exists(index=index_name):
        es.indices.delete(index=index_name)
    print(es.indices.create(index=index_name))



#main
es = Elasticsearch([{'host':es_host, 'port':es_port}], timeout=30)
es.indices.delete(index='analysis', ignore=[400,404])

#elastic_insert(word, word_freq, 1)	
#elastic_search("TF_idf", 1)	
#elastic_insert(word_freq, word, 1)	
#print(elastic_search("TF_idf", 1))
#print(elastic_search("similarity", 1))	
