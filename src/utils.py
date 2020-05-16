import os
from glob import glob
import re

def get_files(file_path, extension):
    if not os.path.exists(file_path):
        print(f"Path {file_path} does not exist...")
        exit(1)
    if not os.path.isdir(file_path) and os.path.isfile(file_path):
        doc_paths = [file_path]
    else:
        doc_paths = glob(file_path + f"/**/*.{extension}", recursive=True)
    if not doc_paths:
        raise Exception(f"Path {doc_paths} not found")
    return doc_paths

def get_valid_filename(s):
    s = str(s).strip().replace(' ', '_')
    return re.sub(r'(?u)[^-\w.]', '', s)