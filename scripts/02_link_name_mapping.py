"""
For each downloaded competition result page in HTML, extract the table containing the links to detailed results,
protocols, judges' information, etc., and create a mapping between the links and their descriptive names.
"""

import json
import logging
import os
import time

import pandas as pd
from bs4 import BeautifulSoup
from file_paths import DATA_PATH, LOG_PATH
from tqdm import tqdm


def extract_table_from_html(file_path):
    soup = BeautifulSoup(
        open(file_path, encoding="utf8"),
        "html.parser",
    )
    tables = soup.find_all("table")

    # only keep leaf-level tables
    tables = [
        table
        for table in tables
        if (not table.find("table")) and ("starting" in str(table).lower())
    ]

    if len(tables) != 1:
        print(f"{file_path}: Extracted more than one table or no table extracted.")

    return tables[0]


def extract_texts_and_links(table):
    text_data = []
    link_data = []
    for row in table.find_all("tr"):
        row_text_data = []
        row_link_data = []
        for cell in row.find_all("td"):
            link = cell.find("a")
            if link:
                row_link_data.append(link["href"])
            else:
                row_link_data.append(None)
            if cell.text != "":
                row_text_data.append(cell.text)
            else:
                row_text_data.append(None)

        text_data.append(row_text_data)
        link_data.append(row_link_data)

    df_text = pd.DataFrame(text_data)
    df_text.ffill(inplace=True)
    df_text.fillna("", inplace=True)
    df_link = pd.DataFrame(link_data)

    return df_text, df_link


def generate_link_name(df_text, df_link, file_path):
    cols_concat = []
    col_count = df_link.shape[1]
    for col_index in range(col_count):
        if df_link.iloc[:, col_index].notna().sum() == 0:
            cols_concat.append(col_index)
    df_text["prefix"] = df_text.iloc[:, cols_concat].agg(" ".join, axis=1)

    for col_index in range(col_count):
        if col_index not in cols_concat:
            df_text.iloc[:, col_index] = (
                df_text["prefix"] + " " + df_text.iloc[:, col_index]
            )
            df_text.iloc[:, col_index] = df_text.iloc[:, col_index].apply(
                lambda x: " ".join(x.split())
            )

    link_dict = dict()
    for row_index in range(df_link.shape[0]):
        for col_index in range(df_link.shape[1]):
            if df_link.iloc[row_index, col_index]:
                link_dict[df_link.iloc[row_index, col_index]] = df_text.iloc[
                    row_index, col_index
                ]

    with open(file_path, "w", encoding="utf-8") as json_file:
        json.dump(link_dict, json_file, indent=4)


def main():
    logging.basicConfig(
        filename=os.path.join(LOG_PATH, "02_unable_to_extract_link_name_mapping.log"),
        format="%(asctime)s - %(levelname)s - %(message)s",
        filemode="w",
        level=logging.INFO,
    )

    start = time.time()

    url_path = os.path.join(DATA_PATH, "urls")
    for dir_name in tqdm(os.listdir(url_path)):
        folder_path = os.path.join(url_path, dir_name)

        if os.path.exists(os.path.join(folder_path, "link_name_mapping.json")):
            continue

        try:
            table = extract_table_from_html(
                os.path.join(folder_path, f"{dir_name}.html")
            )
            df_text, df_link = extract_texts_and_links(table)
            generate_link_name(
                df_text,
                df_link,
                os.path.join(folder_path, "link_name_mapping.json"),
            )
        except Exception as e:
            logging.error(f"Error processing {dir_name}: {e}")

    end = time.time()
    logging.info("Total time taken: {:.2f} minutes".format((end - start) / 60))


if __name__ == "__main__":
    main()
