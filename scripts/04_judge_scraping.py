"""
This script identifies HTML files that contain judge information based on the link_name_mapping.json files created in step 02,
and extracts judge information for each competition and saves the it as pickled DataFrames in the respective competition directories.
"""

import json
import logging
import os
import re
import time
from io import StringIO

import pandas as pd
from bs4 import BeautifulSoup
from file_paths import LOG_PATH, RAW_DATA_PATH
from tqdm import tqdm

RENAME_COLS = {"Nat.": "Nation"}

DISCIPLINES = r"(?:men |women |ladies |pair |pairs |ice dance |ice dancing |synchronized skating )"
PROGRAMS = r"(?:short program|rhythm dance|short dance|compulsory dance|original dance|free skating|free dance|qualifying.{0,30})$"


def match_conditions(tag):
    text = tag.get_text()
    return re.search(DISCIPLINES, text, re.IGNORECASE) and re.search(
        PROGRAMS, text, re.IGNORECASE
    )


def extract_one_table(dir_name, key):
    soup = BeautifulSoup(
        open(os.path.join(RAW_DATA_PATH, dir_name, key), encoding="utf8"),
        "html.parser",
    )

    tables = soup.find_all("table")
    tables = [
        table
        for table in tables
        if ("function" in table.text.lower()) and (table.text.lower() != "isu")
    ]

    df = pd.read_html(StringIO(str(tables[-1])), header=0)[0]
    df.dropna(how="all", inplace=True, axis=0)
    df.rename(
        columns=RENAME_COLS,
        inplace=True,
    )

    # check column names
    if list(df.columns) != ["Function", "Name", "Nation"]:
        logging.warning(
            f"Unexpected columns found in {dir_name} - {key}. Please check the original file."
        )

    df["source"] = key
    df["category"] = soup.body.find_all(match_conditions)[0].text.strip().lower()

    return df


def extract_judge_table(dir_name):
    with open(
        os.path.join(RAW_DATA_PATH, dir_name, "link_name_mapping.json"),
        "r",
        encoding="utf-8",
    ) as json_file:
        data = json.load(json_file)

    dfs = []
    for key, value in data.items():
        if "panel of judges" in value.lower() or "officials" in value.lower():
            if not os.path.isfile(os.path.join(RAW_DATA_PATH, dir_name, key)):
                continue

            try:
                df = extract_one_table(dir_name, key)
            except Exception as e:
                logging.error(f"Error processing {dir_name} - {key}: {e}")
                continue

            dfs.append(df)

    if len(dfs) > 0:
        df_final = pd.concat(dfs)

        df_final.to_pickle(os.path.join(RAW_DATA_PATH, dir_name, "judges.pkl"))


def main():
    logging.basicConfig(
        filename=os.path.join(LOG_PATH, "04_judge_scraping.log"),
        format="%(asctime)s - %(levelname)s - %(message)s",
        filemode="w",
        level=logging.INFO,
    )

    start = time.time()

    for dir_name in tqdm(os.listdir(RAW_DATA_PATH)):
        if os.path.isfile(
            os.path.join(RAW_DATA_PATH, dir_name, "link_name_mapping.json")
        ):
            try:
                extract_judge_table(dir_name)
            except Exception as e:
                logging.error(f"Error processing {dir_name}: {e}")
                continue

    end = time.time()
    logging.info("Total time taken: {:.2f} minutes".format((end - start) / 60))


if __name__ == "__main__":
    main()
