"""
This script downloads the competition result pages as HTML files for all competition links listed in 'data/links/comp_links.csv'.
"""

import logging
import os
import time

import pandas as pd
import requests
from file_paths import DATA_PATH, LOG_PATH
from tqdm import tqdm

LINK_PATH = os.path.join(DATA_PATH, "links")
OUTPUT_PATH = os.path.join(DATA_PATH, "urls")


def download_webpage(url, file_path):
    dir_name = url.split("/")[-2]
    file_path_full = os.path.join(file_path, dir_name)
    if not os.path.exists(file_path_full):
        os.makedirs(file_path_full)

    if os.path.exists(os.path.join(file_path_full, f"{dir_name}.html")):
        return

    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()

        with open(
            os.path.join(file_path_full, f"{dir_name}.html"), "w", encoding="utf-8"
        ) as file:
            file.write(response.text)

    except requests.exceptions.RequestException as e:
        logging.error(f"An error occurred: {e}")


def main():
    logging.basicConfig(
        filename=os.path.join(LOG_PATH, "01_unable_to_download_main_page.log"),
        format="%(asctime)s - %(levelname)s - %(message)s",
        filemode="w",
        level=logging.INFO,
    )

    start = time.time()

    links = pd.read_csv(os.path.join(LINK_PATH, "comp_links.csv"))

    for link in tqdm(links["links"].tolist()):
        download_webpage(link, OUTPUT_PATH)

    end = time.time()
    logging.info("Total time taken: {:.2f} minutes".format((end - start) / 60))


if __name__ == "__main__":
    main()
