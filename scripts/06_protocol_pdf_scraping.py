"""
This script extracts detailed judge-element-level scores from the downloaded protocols (in PDF) for each competition
and saves the it as pickled DataFrames in the respective competition directories.
"""

import json
import logging
import os
import re
import time

import fitz
import pandas as pd
import utils.pdf_scraping as ut
from file_paths import DATA_PATH, LOG_PATH
from tqdm import tqdm
from utils.cleaning import extract_comp_type_season

LINK_PATH = os.path.join(DATA_PATH, "links")
OUTPUT_PATH = os.path.join(DATA_PATH, "urls")


def extract_all_protocols(dir_name, season):
    """Extract all protocols from the given directory and save them as a pickle file."""
    with open(
        os.path.join(OUTPUT_PATH, dir_name, "link_name_mapping.json"),
        "r",
        encoding="utf-8",
    ) as json_file:
        data = json.load(json_file)

    df_disciplines = []
    for key, value in data.items():
        if (
            key.endswith(".pdf")
            and ("score" in value.lower())
            and ("qualifying" not in key.lower())
            and ("synchronized" not in key.lower())
            and ("_qa_" not in key.lower())
            and ("_qb_" not in key.lower())
            and ("preliminaryround" not in key.lower())
        ):
            if not os.path.isfile(os.path.join(OUTPUT_PATH, dir_name, key)):
                continue

            doc = fitz.open(os.path.join(OUTPUT_PATH, dir_name, key))

            # check if the first page is protocol
            if (not "nation" in doc[0].get_text(sort=True).lower()) and (
                not "noc" in doc[0].get_text(sort=True).lower()
            ):
                doc = doc[1:]  # skip the first page if it is not a protocol

            skaters = ut.get_results_all_pages(doc, dir_name, season)

            # convert skaters to dataframes
            dfs = []
            for skater in skaters:
                if skater:
                    skater_result = ut.Skater(skater, dir_name, key, season)
                    df = skater_result.to_dataframe()
                    dfs.append(df)

            # append results, add category and source
            if len(dfs) > 0:
                df = pd.concat(dfs, ignore_index=True)

                if re.search(r"j?gp", dir_name) and season == 2004:
                    df["category"] = value
                else:
                    try:
                        df["category"] = re.findall(
                            r"\b(.*(?:men |women |ladies |pair |pairs |ice dance |ice dancing |synchronized skating ).{0,20}?)(?:\n\n|\s\s)",
                            doc[0].get_text(sort=True).strip().lower(),
                        )[0]
                    except:
                        df["category"] = value

                df["source"] = key

                df_disciplines.append(df)
            else:
                logging.warning(
                    f"No skaters found in {key} in {dir_name}. Skipping this file."
                )

    if len(df_disciplines) > 0:
        df_final = pd.concat(df_disciplines)

        df_final.to_pickle(os.path.join(OUTPUT_PATH, dir_name, "protocols.pkl"))


def main():
    logging.basicConfig(
        filename=os.path.join(LOG_PATH, "06_protocol_pdf_scraping.log"),
        format="%(asctime)s - %(levelname)s - %(message)s",
        filemode="w",
        level=logging.INFO,
    )

    start = time.time()

    for dir_name in tqdm(os.listdir(OUTPUT_PATH)):
        if os.path.isfile(
            os.path.join(OUTPUT_PATH, dir_name, "link_name_mapping.json")
        ):
            _, _, season = extract_comp_type_season(dir_name)
            try:
                extract_all_protocols(dir_name, season)
            except Exception as e:
                logging.error(f"Error processing {dir_name}: {e}")

    end = time.time()
    logging.info("Total time taken: {:.2f} minutes".format((end - start) / 60))


if __name__ == "__main__":
    main()
