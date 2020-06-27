#!/bin/bash
SETUP_DIR="./project"

WEB_DIR="$SETUP_DIR/"templates
ETC_DIR="$SETUP_DIR/"static
IMG_DIR="$IMG_DIR/"img

if [ ! -d "$SETUP_DIR" ]; then
	mkdir -p $WEB_DIR
	mkdir -p $IMG_DIR
fi

cp app.py $SETUP_DIR
cp home.html $WEB_DIR
cp word_analysis.html $WEB_DIR
cp cos_sim.html $WEB_DIR
cp loading_text.gif $IMG_DIR

python -c 'import subprocess
import sys
try:
	import sklearn
except ModuleNotFoundError:
	subprocess.call([sys.executable, "-m", "pip", "install", "scikit-learn"])'
	

cd $SETUP_DIR

./app.py
