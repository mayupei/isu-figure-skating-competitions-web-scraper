"""
This script appends the detailed judge-element-level scores from all competitions and cleans the data.
"""

import os
import re

import numpy as np
import pandas as pd
from file_paths import CLEANED_DATA_PATH, RAW_DATA_PATH
from utils.cleaning import (
    extract_comp_type_season,
    extract_discipline,
    extract_program,
    generate_junior_indicator,
)


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
    for dir_name in os.listdir(RAW_DATA_PATH):
        if os.path.isfile(os.path.join(RAW_DATA_PATH, dir_name, "protocols.pkl")):
            df = pd.read_pickle(os.path.join(RAW_DATA_PATH, dir_name, "protocols.pkl"))
            if not df.empty:
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

    ### pivot the data and standardize judge scores
    judge_cols = [col for col in df.columns if re.search(r"^j\d+$", col)]
    for col in judge_cols:
        df[col] = pd.to_numeric(
            df[col].astype(str).str.replace(",", "."), errors="coerce"
        )

    id_vars = [col for col in df.columns if col not in judge_cols]
    df = pd.melt(
        df,
        id_vars=id_vars,
        value_vars=judge_cols,
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

    df.to_pickle(os.path.join(CLEANED_DATA_PATH, "protocols.pkl"))


if __name__ == "__main__":
    main()
