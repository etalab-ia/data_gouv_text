#!/usr/bin/env bash
RESOURCE_CSV="./data/resources.csv"
DOWNLOAD_OUTPUT="./output/"
FILE_TYPE="pdf"
TXT_OUTPUT="./output"

eval "$(conda shell.bash hook)"
conda activate data_gouv_text


echo "Download pdf files"
python src/download_files.py $RESOURCE_CSV $DOWNLOAD_OUTPUT $FILE_TYPE

echo "Transform to text"
python src/pdf2txt.py $DOWNLOAD_OUTPUT $TXT_OUTPUT
