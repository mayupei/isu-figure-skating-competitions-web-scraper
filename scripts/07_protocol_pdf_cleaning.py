"""
This script appends the detailed judge-element-level scores from all competitions and cleans the data.
"""

import os

import numpy as np
import pandas as pd
from file_paths import DATA_PATH
from utils.cleaning import (
    extract_comp_type_season,
    extract_discipline,
    extract_program,
    generate_junior_indicator,
)

INPUT_PATH = os.path.join(DATA_PATH, "urls")
OUTPUT_PATH = os.path.join(DATA_PATH, "raw")
JUDGE_COLS = [
    "j1",
    "j2",
    "j3",
    "j4",
    "j5",
    "j6",
    "j7",
    "j8",
    "j9",
    "j10",
    "j11",
    "j12",
    "j13",
]


def standardize_score(col):
    if col.notna().sum() == 0:
        return col
    mean = np.mean(col)
    std = np.std(col)

    if std != 0:
        return (col - mean) / std

    return [0 if not np.isnan(c) else np.nan for c in col]


def main():
    ### append all files
    dfs = []
    for dir_name in os.listdir(INPUT_PATH):
        if os.path.isfile(os.path.join(INPUT_PATH, dir_name, "protocols.pkl")):
            df = pd.read_pickle(os.path.join(INPUT_PATH, dir_name, "protocols.pkl"))
            df["comp"] = dir_name
            dfs.append(df)

    df = pd.concat(dfs, ignore_index=True)

    ### Clean up the data; add new columns
    df["category"] = df["category"].str.lower()
    df["discipline"] = df["category"].apply(extract_discipline)
    df["program"] = df.apply(
        lambda row: extract_program(row["category"], row["source"]), axis=1
    )

    df["comp_type"], df["year"], df["season"] = zip(
        *df["comp"].apply(extract_comp_type_season)
    )
    df["junior"] = df.apply(
        lambda row: generate_junior_indicator(row["category"], row["comp_type"]), axis=1
    )
    df["deductions"] = df["deductions"].apply(np.abs)
    df["team"] = df["source"].apply(lambda x: "team" in x.lower())

    print(
        "Check if 'comp', 'discipline', 'program', 'junior', 'team' can uniquely identify a competition."
    )
    print(
        df.groupby(["comp", "discipline", "program", "junior", "team"])["source"]
        .nunique()
        .value_counts()
    )

    ### pivot the data and standardize judge scores
    for col in JUDGE_COLS:
        df[col] = pd.to_numeric(
            df[col].astype(str).str.replace(",", "."), errors="coerce"
        )

    id_vars = [col for col in df.columns if col not in JUDGE_COLS]
    df = pd.melt(
        df,
        id_vars=id_vars,
        value_vars=JUDGE_COLS,
        var_name="judge_id",
        value_name="judge_score",
    )

    df["judge_score_std"] = df.groupby(
        ["comp", "source", "rank", "element", "element_order"], dropna=False
    )["judge_score"].transform(standardize_score)
    df.sort_values(
        by=["comp", "source", "rank", "element_order", "element", "judge_id"],
        inplace=True,
    )

    # replace the skater's nation as RUS (Russian) is the nation is OAR and ROC
    df["nation"] = df["nation"].apply(lambda x: "RUS" if x in ("OAR", "ROC") else x)

    df.to_pickle(os.path.join(OUTPUT_PATH, "protocols.pkl"))


if __name__ == "__main__":
    main()
