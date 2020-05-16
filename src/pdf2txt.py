'''Converts input pdf files into text

Usage:
    pdf2txt.py <i> <o>  [options]

Arguments:
    <i>             An path of a pdf or a folder with pdfs to convert
    <o>             The folder path where the text files are gonna be stored
    --cores CORES   The number of cores to use in a parallel setting [default: 1:int]
'''
import os
import tempfile

import pdfbox
import pyocr.builders
from pdf2image import convert_from_path
from tqdm import tqdm
from argopt import argopt
from joblib import Parallel, delayed

from utils import get_files

P = pdfbox.PDFBox()
TOOL = pyocr.get_available_tools()[0]
BUILDER = pyocr.builders.TextBuilder()


def pdf2image(doc_path):
    with tempfile.TemporaryDirectory() as path:
        print(f"Transforming file {doc_path} to image")
        images_from_path = convert_from_path(doc_path, output_folder=path)
    return images_from_path


def ocr_pdf(doc_path):
    try:
        images = pdf2image(doc_path)
        txt = ""
        for i, img in enumerate(images):
            img = img.convert('L')
            print(f"\tOCRizing image {i} of file {doc_path}.")
            txt += TOOL.image_to_string(img, lang="fra", builder=BUILDER)
        return txt
    except Exception as e:
        print(f"Could not OCRize file {doc_path}: {e}")


def file_is_empty(doc_path):
    if os.path.getsize(doc_path) < 20:
        return True
    else:
        return False


def pdf2txt(doc_path):
    try:
        P.extract_text(doc_path)  # writes text to /path/to/my_file.txt
        txt_path = doc_path[:-4] + ".txt"
        if file_is_empty(txt_path):
            # Text file is very small, PDF has an image probably, try OCRizing it
            ocr_txt = ocr_pdf(doc_path)
            with open(txt_path, "w") as filo:
                filo.write(ocr_txt)
        return 1
    except Exception as e:
        print(f"Could not convert to txt file {doc_path}")
        return 0


if __name__ == '__main__':
    parser = argopt(__doc__).parse_args()
    file_path = parser.i
    output_folder = parser.o
    n_jobs = int(parser.cores)

    doc_paths = get_files(file_path, extension="pdf")
    print(f"Got {len(doc_paths)} files to process")
    if n_jobs > 1:
        success_transformed = Parallel(n_jobs=n_jobs, backend="multiprocessing")(
            delayed(pdf2txt)(path) for path in tqdm(doc_paths))
    else:
        success_transformed = []
        for path in tqdm(doc_paths):
            success_transformed.append(pdf2txt(path))

    print(f"I successfully transformed {str(sum(success_transformed))}  of {len(success_transformed)} files")
