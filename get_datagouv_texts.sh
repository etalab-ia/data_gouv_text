#!/usr/bin/env bash

eval "$(conda shell.bash hook)"
conda activate data_gouv_text

echo "Download pdf files"
python src/download_files.py output output

echo "Transform to text"
python src/pdf2txt.py output output
