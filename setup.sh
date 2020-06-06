#!/bin/bash

SETUP_DIR="./project"

WEB_DIR="$SETUP_DIR/"templates
ETC_DIR="$SETUP_DIR/"static

if [ ! -d "$SETUP_DIR" ]; then
	mkdir -p $WEB_DIR
	mkdir $ETC_DIR
fi
	
cp app.py $SETUP_DIR	
cp home.html $WEB_DIR
cp listPrint.html $WEB_DIR
cp word_analysis.html $WEB_DIR
cd $SETUP_DIR

flask run
