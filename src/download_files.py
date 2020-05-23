'''Downloads the resources of the specified type found in a catalog csv  and saves it with the resource and its dataset id

Usage:
    csv_downloader.py <i> <o> <t> [options]

Arguments:
    <i>             An input csv that contains a resource catalog csv (typicaly from data.gouv.fr)
    <o>             The folder path where the files are gonna be downloaded
    <t>             The filetype we want to download
    --n NFILES      Number of files to download [default: None:int]
    --max_size MAX  Download at most MAX bytes from a file [default: None:int]
    --cores CORES   The number of cores to use in a parallel setting [default: 1:int]
'''
import os
import resource
import subprocess
from pathlib import Path

from tqdm import tqdm
import pandas as pds
from argopt import argopt
from joblib import Parallel, delayed
import unidecode

from utils import get_valid_filename
from urllib3 import PoolManager
import re
MB = 1000000


def download_file(url, downloaded_file_path, max_bytes=100):
    pool = PoolManager()
    response = pool.request("GET", url, preload_content=False, timeout=10, retries=3, redirect=True)
    if response.status > 299:
        raise Exception(f"Got 404 for url:{url}")
    chunk_to_save_raw = response.read(max_bytes)
    if not chunk_to_save_raw:
        raise Exception("Could not read anything from url")
    small_chunk: str = response.read(MB)
    last_line = re.split(b"\r?\n", small_chunk, maxsplit=1)[0]
    chunk_to_save = chunk_to_save_raw + last_line
    with open(downloaded_file_path, "wb") as filo:
        filo.write(chunk_to_save)
    tqdm.write(f"\tDownloaded file to {downloaded_file_path}")
    response.release_conn()
    return 1

def is_compressed(url):
    splitted_url = url.split(".")
    for ext in ["zip", "gz"]:
        if ext in splitted_url[-1]:
            return ext


def downloader(url, id, organization, output_folder, file_type, max_size):
    # url = "https://erdf.opendatasoft.com/explore/dataset/reseauoo-bt/download?format=csv&timezone=Europe/Berlin&use_labelos_for_header=true"
    def preexec_fn():
        if max_size:
            resource.setrlimit(resource.RLIMIT_FSIZE, (max_size, max_size))

    downloaded_file_size = -1
    downloaded_file_path = Path("")
    try:
        possible_file_type = is_compressed(url)
        if not possible_file_type:
            extension = file_type
        new_output_folder = os.path.join(output_folder, organization)
        if not os.path.exists(new_output_folder):
            os.mkdir(new_output_folder)
        print(f"Downloading file with id {id}")
        downloaded_file_path = Path(f"{new_output_folder}/{id}.{extension}")
        if downloaded_file_path.exists():
            print(f"File with id {id} already exists! Not downloading.")
            return 0

        # Download file
        download_status = download_file(url=url, downloaded_file_path=downloaded_file_path, max_bytes=100)
        # p = subprocess.Popen(
        #     ["wget", "--timeout", "10", "--no-check-certificate", "--tries", "3", "-O", downloaded_file_path, url],
        #     preexec_fn=preexec_fn)
        # p.communicate()  # now wait plus that you can send commands to process
        # downloaded_file_size = downloaded_file_path.stat().st_size

        if not download_status:
            return 0
        else:
            return 1
    except Exception as e:
        print(f"Could not download file with id {id}\n\t{str(e)}")
        return 0
    finally:
        if not downloaded_file_size:
            downloaded_file_path.unlink()


def get_files(file_path, output_folder, file_type, download_n_files, max_size=None, n_jobs=1):
    df = pds.read_csv(file_path, sep=";").sample(frac=1)

    # naively filter the df to get only the desired file_type
    df = df[df.format == file_type]
    if download_n_files:
        df = df.iloc[:download_n_files]
    print(f"There are {len(df)} resources of type {file_type}")
    urls = df["url"].values
    resource_ids = df["id"].values
    dataset_ids = df["dataset.id"].values
    new_ids = dataset_ids + "--" + resource_ids
    organizations = df["dataset.organization"].fillna("NA").apply(
        lambda x: unidecode.unidecode(get_valid_filename(x))).values
    assert len(urls) == len(new_ids)

    if n_jobs > 1:
        succes_downloaded = Parallel(n_jobs=n_jobs)(
            delayed(downloader)(url, id, org, output_folder, file_type, max_size) for url, id, org in
            tqdm(list(zip(urls, new_ids, organizations))))
    else:
        succes_downloaded = []
        for url, id, org in tqdm(list(zip(urls, new_ids, organizations))):
            succes_downloaded.append(downloader(url, id, org, output_folder, file_type, max_size))
    print(f"I successfully downloaded {sum(succes_downloaded)} of {len(succes_downloaded)} files")


if __name__ == '__main__':
    parser = argopt(__doc__).parse_args()
    file_path = parser.i
    output_folder = parser.o
    file_type = parser.t
    download_n_files = parser.n
    max_size = parser.max_size
    n_jobs = int(parser.cores)

    get_files(file_path, output_folder, file_type, download_n_files, max_size, n_jobs)
