import logging
import re

import pandas as pd


def convert_to_float(text):
    """Convert a string to float if possible, otherwise return the string."""
    try:
        return float(text)
    except ValueError:
        return text


def refine_column_split(line):
    """for example, if a column is 5.3 x, split it to 5.3 and x"""
    new_line = []
    for item in line:
        if isinstance(item, (int, float)):
            new_line.append(item)
            continue
        items = item.split(" ")
        if re.search(r"^\d+(\.\d+)?$", items[0]):
            new_line += [convert_to_float(i) for i in items]
        else:
            new_line.append(item)
    return new_line


def split_line_to_columns(line, comp, season):
    """Split lines to columns and only keep relevant lines."""
    line = line.split("  ")
    line = [i.strip() for i in line]
    result = [convert_to_float(i) for i in line if i != ""]

    if re.search(r"j?gp", comp) and season == 2004:
        result.reverse()

    if not result:
        return None
    if not isinstance(result[-1], float):
        return None

    # fix wrongly parsed first columns
    if (not isinstance(result[0], float)) and result[0][0].isdigit():
        result = result[0].split(" ", 1) + result[1:]
        result[0] = convert_to_float(result[0])

    # all floats and integers should be in a single column
    result = refine_column_split(result)

    return result


def get_results_all_pages(doc, comp, season):
    """Extract results from all pages of the document and separate to skaters."""
    ### extract texts
    results = []
    for page in doc:
        results += page.get_text(sort=True).splitlines()

    lines = []
    for line in results:
        line = split_line_to_columns(line, comp, season)
        if line:
            lines.append(line)

    if re.search(r"j?gp", comp) and season == 2004:
        lines.reverse()

    ### separate skaters
    new_skater_index = []
    for i, line in enumerate(lines[:-1]):
        if isinstance(line[0], str) and isinstance(lines[i + 1][0], float):
            new_skater_index.append(i + 1)

    if not new_skater_index:
        return [lines]

    ### seperate skaters
    skaters = []
    current_index = 0
    for index in new_skater_index:
        skaters.append(lines[current_index:index])
        current_index = index
    skaters.append(lines[current_index:])

    return skaters


def find_marks(row):
    """Find marks in the row."""
    marks = []
    for item in row[2:]:
        if isinstance(item, str) and (
            re.search(r"^([!qe<*>SFxX][|\s]?)*[!qe<*>SFxX]$", item)
        ):
            marks.append(item)
    return marks


def remove_info(row):
    """Remove info from the row."""
    for index, item in enumerate(row):
        if isinstance(item, float):
            continue
        if item == "Info":
            row.remove(item)
        elif "Info" in item:
            row[index] = item.replace("Info", "")
    return row


def fix_first_row(row, dir_name, file_name, season):
    """Extract the first row from the result."""
    correct_length = 7
    if season >= 2009 or dir_name in ("wjc2009", "wc2009"):
        correct_length = 8

    if len(row) != correct_length:
        if (sum(isinstance(item, str) for item in row) == 1) and len(
            row
        ) == correct_length - 1:
            # if the first row is all strings, it is likely a header row
            row = [row[0]] + row[1].rsplit(" ", 1) + row[2:]
        else:
            raise Exception(
                f"{dir_name} - {file_name}: The first row is {row}. Wrong column count."
            )
    return row


class Skater:
    """Class to represent a skater."""

    def __init__(self, result, dir_name, file_name, season):
        self.result = result
        self.dir_name = dir_name
        self.file_name = file_name
        self.season = season

    def split_result(self):
        """Split the result into the first row, TES and PCS."""
        first_row = fix_first_row(
            self.result[0], self.dir_name, self.file_name, self.season
        )
        tes = first_row[-3]
        pcs = first_row[-2]

        tes_index = None
        pcs_index = None
        for i, item in enumerate(self.result):
            if tes_index is None:
                if item[-1] == tes and len(item) == 2:
                    tes_index = i
            elif item[-1] == pcs and len(item) == 2:
                pcs_index = i
                if tes_index is not None:
                    break

        if (tes_index is None) or (pcs_index is None):
            raise Exception(
                f"{self.dir_name} - {self.file_name}: Failed to separate TES and PCS for {self.result}"
            )

        self.first_row = first_row
        self.tes = self.result[1:tes_index]
        self.pcs = self.result[tes_index + 1 : pcs_index]

    def tes_to_dataframe(self):
        """Convert TES to a DataFrame."""
        for row in self.tes:
            if (
                isinstance(row[0], float)
                and row[0] == 0
                and isinstance(row[1], float)
                and row[1] == 0
            ):
                row.insert(0, "0")
                row.insert(1, "Invalid")
            elif not isinstance(row[1], str):
                row.insert(1, "Invalid")

        marks = [None] * len(self.tes)
        second_half = [None] * len(self.tes)
        for i, item in enumerate(self.tes):
            # remove info
            item = remove_info(item)

            if ("x" in item[2:]) or ("X" in item[2:]):
                second_half[i] = "x"
                if "x" in item[2:]:
                    item.remove("x")
                if "X" in item[2:]:
                    item.remove("X")
            mark = find_marks(item)
            if mark:
                for m in mark:
                    item.remove(m)
                marks[i] = " ".join(mark)

        # check if all items have the same length
        max_length = max(len(item) for item in self.tes)
        if not all(len(item) == max_length for item in self.tes):
            logging.info(
                f"TES items have different lengths for {self.dir_name} - {self.file_name}"
            )
            logging.info(self.first_row)
            for item in self.tes:
                logging.info(item)

        columns = (
            ["element_order", "element", "base_value", "goe"]
            + [f"j{i}" for i in range(1, max_length - 4)]
            + ["panel_score"]
        )
        df_tes = pd.DataFrame(self.tes, columns=columns)
        df_tes["marks"] = marks
        df_tes["second_half"] = second_half
        df_tes["component"] = "TES"

        self.df_tes = df_tes

    def pcs_to_dataframe(self):
        """Convert PCS to a DataFrame."""
        # sanity check: each item should have the same number of elements
        max_length = max(len(item) for item in self.pcs)
        columns = (
            ["element", "factor"]
            + [f"j{i}" for i in range(1, max_length - 2)]
            + ["panel_score"]
        )
        if not all(len(item) == max_length for item in self.pcs):
            logging.info(
                f"PCS items have different lengths for {self.dir_name} - {self.file_name}"
            )
            logging.info(self.first_row)
            for item in self.pcs:
                logging.info(item)

        df_pcs = pd.DataFrame(self.pcs, columns=columns)
        df_pcs["component"] = "PCS"
        self.df_pcs = df_pcs

    def to_dataframe(self):
        """Convert the skater's data to a DataFrame."""
        ### extract first row, tes and pcs
        self.split_result()
        self.tes_to_dataframe()
        self.pcs_to_dataframe()

        df = pd.concat([self.df_tes, self.df_pcs], ignore_index=True)

        ### common columns
        df["rank"] = self.first_row[0]
        df["name"] = self.first_row[1]
        df["nation"] = self.first_row[2]
        if self.season >= 2009 or self.dir_name in ("wjc2009", "wc2009"):
            df["stn"] = self.first_row[3]
        else:
            df["stn"] = None
        df["tss"] = self.first_row[-4]
        df["tes"] = self.first_row[-3]
        df["pcs"] = self.first_row[-2]
        df["deductions"] = self.first_row[-1]

        return df
