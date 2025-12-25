"""
This script downloads detailed competition results, protocols and judges' information based on the link_name_mapping.json files
created in the previous step. The files are saved as HTML or PDF in the respective competition directories.
"""

import json
import logging
import os
import re
import time

import pandas as pd
import requests
from file_paths import LINKS_PATH, LOG_PATH, RAW_DATA_PATH
from tqdm import tqdm


def download_html_or_pdf(root_url, url, dir_path):
    if os.path.exists(os.path.join(dir_path, url)):
        return

    if "/" in url:
        url = url.split("/")[-1]

    if re.search(r"/$", root_url):
        url_path_full = root_url + url
    elif re.search(r"index.htm$", root_url):
        root_url = re.sub(r"index.htm$", "", root_url)
        url_path_full = root_url + url
    else:
        url_path_full = root_url + "/" + url

    response = requests.get(url_path_full, timeout=60)
    response.raise_for_status()

    if url.endswith("pdf"):
        with open(os.path.join(dir_path, url), "wb") as pdf_file:
            pdf_file.write(response.content)
    else:
        with open(os.path.join(dir_path, url), "w", encoding="utf-8") as file:
            file.write(response.text)


def download_all_results_for_one_competition(dir_name, root_url):
    with open(
        os.path.join(RAW_DATA_PATH, dir_name, "link_name_mapping.json"),
        "r",
        encoding="utf-8",
    ) as json_file:
        data = json.load(json_file)

    for url in data.keys():
        try:
            download_html_or_pdf(root_url, url, os.path.join(RAW_DATA_PATH, dir_name))
        except Exception as e:
            logging.error(f"Error downloading {root_url} {url}: {e}")


def main():
    logging.basicConfig(
        filename=os.path.join(LOG_PATH, "03_download_results_to_html_or_pdf.log"),
        format="%(asctime)s - %(levelname)s - %(message)s",
        filemode="w",
        level=logging.INFO,
    )

    start = time.time()

    link = pd.read_csv(LINKS_PATH)
    link["comp"] = link["links"].apply(lambda x: x.split("/")[-2])
    link_dict = dict()
    for _, row in link.iterrows():
        link_dict[row["comp"]] = row["links"]

    for dir_name in tqdm(os.listdir(RAW_DATA_PATH)):
        root_url = link_dict[dir_name]
        if os.path.isfile(
            os.path.join(RAW_DATA_PATH, dir_name, "link_name_mapping.json")
        ):
            download_all_results_for_one_competition(dir_name, root_url)

    end = time.time()
    logging.info("Total time taken: {:.2f} minutes".format((end - start) / 60))


if __name__ == "__main__":
    main()
