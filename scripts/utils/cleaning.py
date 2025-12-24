import re


def extract_comp_type_season(comp):
    if comp == "jgp5pol2022":
        comp = "jgppol2022"
    match = re.search(r"^([a-zA-Z]+)(\d+)$", comp)
    comp_name = match.group(1).lower()
    year = match.group(2)

    # comp type
    if re.search(r"^gp\w{3}", comp_name) or (
        comp_name in ("coc", "cor", "nhk", "sa", "sc", "tll")
    ):
        comp_name = "gp"
    elif re.search(r"^jgp\w{3}", comp_name):
        comp_name = "jgp"

    # get year
    if year == "22021":
        year = 2021
    elif len(year) == 2:
        year = int("20" + year)
    elif re.search(r"20\d{2}", year):
        year = int(year)
    elif re.search(r"\d{4}", year):
        if comp_name in ("gp", "jgp", "gpf", "jgpf"):
            year = int("20" + year[:2])
        else:
            year = int("20" + year[-2:])

    # return season
    if comp_name in ("gp", "jgp", "gpf", "jgpf"):
        season = year
    else:
        season = year - 1

    return comp_name, year, season


def extract_discipline(category):
    if ("women" in category) or ("ladies" in category):
        return "women"
    if "men" in category:
        return "men"
    if "pair" in category:
        return "pair"
    if "ice danc" in category:
        return "ice dance"


def extract_program(category, source):
    if (
        ("short program" in category)
        or ("rhythm dance" in category)
        or ("short dance" in category)
        or ("compulsory dance" in category)
    ):
        return "sp"
    if ("free skating" in category) or ("free dance" in category):
        return "lp"
    if "original dance" in category:
        return "od"

    source = source.lower()
    if (
        ("_sp_" in source)
        or ("_rd_" in source)
        or ("_sd_" in source)
        or ("-qual" in source)
        or ("_cd_" in source)
    ):
        return "sp"
    if ("_fs_" in source) or ("_fd_" in source) or ("-fnl" in source):
        return "lp"
    if "_od_" in source:
        return "od"


def generate_junior_indicator(category, comp_name):
    if comp_name in ("wjc", "jgp", "jgpf", "wyog") or ("junior" in category):
        return True

    return False
