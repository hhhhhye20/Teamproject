#!/bin/bash
SETUP_DIR="./project"

WEB_DIR="$SETUP_DIR/"templates
ETC_DIR="$SETUP_DIR/"static

ELA_DIR="./elasticsearch-7.6.2"
if [ ! -d "$SETUP_DIR" ]; then
	mkdir -p $WEB_DIR
	mkdir $ETC_DIR
fi

cp app.py $SETUP_DIR
cp home.html $WEB_DIR
cp word_analysis.html $WEB_DIR

if [ ! -d "$ELA_DIR" ]; then
	echo "ERROR : Elasticsearch을 찾을 수 없습니다. 현재 위치에 elasticsearch-7.6.2 폴더가 있는지 확인해 주세요."
else
	cd $ELA_DIR
	./bin/elasticsearch -d
	cd ..
fi

cd $SETUP_DIR

flask run
