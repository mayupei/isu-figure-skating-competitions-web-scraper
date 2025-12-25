"""
This script appends the judge information from all competitions and cleans the data.
"""

import os
import re

import pandas as pd
from file_paths import CLEANED_DATA_PATH, RAW_DATA_PATH
from utils.cleaning import (
    extract_comp_type_season,
    extract_discipline,
    extract_program,
    generate_junior_indicator,
)


def get_gender(name):
    if re.search(r"Mr(\.|\s)", name):
        return "M"
    if re.search(r"(Ms|Mrs)(\.|\s)", name):
        return "F"


def first_name_first(name):
    ### manual adjustment for two names
    if name == "van VEEN Wilhelmina":
        return "Wilhelmina VAN VEEN"
    if name == "de LACROIX Pierre":
        return "Pierre DE LACROIX"
    names = name.split(" ")
    first_name = []
    last_name = []

    for n in names:
        if n.isupper() and len(n) > 1:
            last_name.append(n)
        else:
            first_name.append(n)
    return " ".join(first_name + last_name)


def main():
    ### append all files
    dfs = []
    for dir_name in os.listdir(RAW_DATA_PATH):
        if os.path.isfile(os.path.join(RAW_DATA_PATH, dir_name, "judges.pkl")):
            df = pd.read_pickle(os.path.join(RAW_DATA_PATH, dir_name, "judges.pkl"))
            if not df.empty:
                df["comp"] = dir_name
                dfs.append(df)

    df = pd.concat(dfs, ignore_index=True)

    ### clean data, extract gender from name
    df["gender"] = df["Name"].apply(get_gender)
    df["Name"] = df["Name"].str.replace(r"\s", " ", regex=True)
    df["Name"] = df["Name"].str.replace(r"^(Ms|Mrs|Mr)(\.\s|\s)", "", regex=True)
    df["Name"] = df["Name"].str.replace(r"(\.)", "", regex=True)
    df["Name"] = df["Name"].apply(first_name_first)

    ### get judge id, clean functions
    df["judge_id"] = df["Function"].str.extract(r"Judge No.(\d+)")
    df["judge_id"] = df["judge_id"].apply(lambda x: "j" + x if pd.notna(x) else x)
    df["Function"] = df["Function"].str.replace(r" No.\d+", "", regex=True)

    ### replace nation as RUS if the nation is OAR (olympic athlete from Russia)
    df["Nation"] = df["Nation"].apply(lambda x: "RUS" if x in ("OAR", "ROC") else x)

    ### the judge nation is missing for some competitions; for those cases, try to get the
    ### judge's nation based on the nation information from other competitions for the same judge
    df_name = df[df["Nation"] != "ISU"][["Name", "Nation"]].drop_duplicates()
    df_name["count"] = df_name.groupby("Name")["Nation"].transform("count")
    df_name = df_name[df_name["count"] == 1][["Name", "Nation"]]

    df_name.rename(columns={"Nation": "Nation2"}, inplace=True)
    df = df.merge(df_name, on="Name", how="left")
    df["Nation2"] = df.apply(
        lambda row: (
            row["Nation"]
            if (row["Nation"] != "ISU") and pd.isna(row["Nation2"])
            else row["Nation2"]
        ),
        axis=1,
    )

    ### check how many judges are assigned nationality
    df_judge = df[df["Function"] == "Judge"].copy()

    ### generate other columns; clean up the data
    df_judge["comp_type"], df_judge["year"], df_judge["season"] = zip(
        *df_judge["comp"].apply(extract_comp_type_season)
    )

    df_judge["category"] = df_judge["category"].str.lower()
    df_judge = df_judge[
        ~df_judge["category"].str.contains(
            "(?:qualifying|preliminary round|synchronized skating)"
        )
    ]

    df_judge["discipline"] = df_judge["category"].apply(extract_discipline)
    df_judge["program"] = df_judge.apply(
        lambda row: extract_program(row["category"], row["source"]), axis=1
    )

    df_judge["junior"] = df_judge.apply(
        lambda row: generate_junior_indicator(row["category"], row["comp_type"]), axis=1
    )

    df_judge["team"] = df_judge["category"].apply(lambda x: "team" in x.lower())

    df_judge.to_pickle(os.path.join(CLEANED_DATA_PATH, "judges.pkl"))


if __name__ == "__main__":
    main()
