import os

BASE_PATH = "[[INSERT YOUR PATH HERE]]"

DATA_PATH = os.path.join(BASE_PATH, "data")
LINKS_PATH = os.path.join(DATA_PATH, "links", "comp_links.csv")
RAW_DATA_PATH = os.path.join(DATA_PATH, "raw")
CLEANED_DATA_PATH = os.path.join(DATA_PATH, "cleaned")

LOG_PATH = os.path.join(BASE_PATH, "logs")
