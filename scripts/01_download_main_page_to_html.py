"""
This script downloads the competition result pages as HTML files for all competition links listed in 'data/links/comp_links.csv'.
"""

import logging
import os
import time

import pandas as pd
import requests
from file_paths import LINKS_PATH, LOG_PATH, RAW_DATA_PATH
from tqdm import tqdm


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
        filename=os.path.join(LOG_PATH, "01_download_main_page_to_html.log"),
        format="%(asctime)s - %(levelname)s - %(message)s",
        filemode="w",
        level=logging.INFO,
    )

    start = time.time()

    links = pd.read_csv(LINKS_PATH)

    for link in tqdm(links["links"].tolist()):
        download_webpage(link, RAW_DATA_PATH)

    end = time.time()
    logging.info("Total time taken: {:.2f} minutes".format((end - start) / 60))


if __name__ == "__main__":
    main()
