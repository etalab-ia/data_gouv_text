'''Downloads the resources of the specified type found in a catalog csv  and saves it with the resource and its dataset id

Usage:
    csv_downloader.py <i> <o> <t> [options]

Arguments:
    <i>             An input csv that contains a resource catalog csv (typicaly from data.gouv.fr)
    <o>             The folder path where the files are gonna be downloaded
    <t>             The filetype we want to download
    --cores CORES   The number of cores to use in a parallel setting [default: 1:int]
'''
import os
import subprocess
from tqdm import tqdm
import pandas as pds
from argopt import argopt
from joblib import Parallel, delayed
import unidecode

from src.utils import get_valid_filename


def is_compressed(url):
    splitted_url = url.split(".")
    for ext in ["zip", "gz"]:
        if ext in splitted_url[-1]:
            return ext


def downloader(url, id, organization, output_folder, file_type):
    try:
        possible_file_type = is_compressed(url)
        if not possible_file_type:
            extension = file_type
        new_output_folder = os.path.join(output_folder, organization)
        if not os.path.exists(new_output_folder):
            os.mkdir(new_output_folder)
        print(f"Downloading file with id {id}")
        p = subprocess.Popen(["wget", "--timeout", "10", "--tries", "3", "-O", "{0}/{1}.{2}".format(new_output_folder, id, extension), url])
        p.communicate()  # now wait plus that you can send commands to process
        if not p.returncode:
            return 1
        else:
            return 0
    except:
        print(f"Could not download file with id {id}")
        return 0


def get_files(file_path, output_folder, file_type, n_jobs):
    df = pds.read_csv(file_path, sep=";").sample(frac=1)

    # naively filter the df to get only the desired file_type
    df = df[df.format == file_type].iloc[:20]
    print(f"There are {len(df)} resources of type {file_type}")
    urls = df["url"].values
    resource_ids = df["id"].values
    dataset_ids = df["dataset.id"].values
    new_ids = dataset_ids + "--" + resource_ids
    organizations = df["dataset.organization"].fillna("NA").apply(lambda x: unidecode.unidecode(get_valid_filename(x))).values
    assert len(urls) == len(new_ids)

    if n_jobs > 1:
        succes_downloaded = Parallel(n_jobs=n_jobs)(
            delayed(downloader)(url, id, org, output_folder, file_type) for url, id, org in tqdm(list(zip(urls, new_ids, organizations))))
    else:
        succes_downloaded = []
        for url, id, org in tqdm(list(zip(urls, new_ids, organizations))):
            succes_downloaded.append(downloader(url, id, org, output_folder, file_type))

    print(f"I successfully downloaded {sum(succes_downloaded)} of {len(succes_downloaded)} files")


if __name__ == '__main__':
    parser = argopt(__doc__).parse_args()
    file_path = parser.i
    output_folder = parser.o
    file_type = parser.t
    n_jobs = int(parser.cores)

    get_files(file_path, output_folder, file_type, n_jobs)
