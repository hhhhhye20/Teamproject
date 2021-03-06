#!/bin/bash
SETUP_DIR="./project"

WEB_DIR="$SETUP_DIR/"templates
ETC_DIR="$SETUP_DIR/"static
IMG_DIR="$ETC_DIR/"img
CSS_DIR="$ETC_DIR/"css
JS_DIR="$ETC_DIR/"js

mkdir -p $WEB_DIR
mkdir -p $IMG_DIR
mkdir -p $CSS_DIR
mkdir -p $JS_DIR

cp app.py $SETUP_DIR
cp home.html $WEB_DIR
cp word_analysis.html $WEB_DIR
cp cos_sim.html $WEB_DIR
cp loading_text.gif $IMG_DIR
cp style_home.css $CSS_DIR
cp cos.css $CSS_DIR
cp style_word.css $CSS_DIR
cp popup.js $JS_DIR
cp Knuemblem.png $IMG_DIR

python -c 'import subprocess
import sys
try:
	import sklearn
except ModuleNotFoundError:
	subprocess.call([sys.executable, "-m", "pip", "install", "scikit-learn"])'
	

cd $SETUP_DIR

./app.py
