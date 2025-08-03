import os
import pickle
import sys
from pathlib import Path
from pkgutil import get_data

import tomli
import yaml

CURRENT_DIR = Path(__file__).resolve().parent       # src/generichelpers/configs
BASE_DIR = CURRENT_DIR.parent                       # src/generichelpers

with open(f'{CURRENT_DIR}/config.yaml', 'r') as f:
    CONFIG = yaml.safe_load(f)

with open(f'{BASE_DIR}/.streamlit/secrets.toml', 'rb') as f:
    SECRETS = tomli.load(f)

sys.path = [p for i in range(1, 4) if (p := os.path.abspath(Path(__file__).parents[i])) not in sys.path] + sys.path

config_folder, data_folder = 'generichelpers.configs', 'generichelpers.data'
CONFIG = yaml.safe_load(get_data(config_folder, 'config.yaml').decode())
ENGLISH_WORDS = set(pickle.loads(get_data(data_folder, 'english_words.p'))["ENGLISH_WORDS"])
HEADERS = {'Content-Type': 'application/json'}

# Mapping seconds to different units
SECONDS_UNITS_MAP = {
    'Y': 31557600,  # 1 year (average considering leap years)
    'Q': 7889400,   # 1 quarter (average)
    'M': 2629800,   # 1 month (average)
    'W': 604800,    # 1 week
    'D': 86400,     # 1 day
    'h': 3600,      # 1 hour
    'm': 60,        # 1 minute
    's': 1          # 1 second
}

# Map time units to pretty names -- full
TIME_KEYS_MAP_FULL = {
    'Y': 'Year',
    'Q': 'Qtr',
    'M': 'Month',
    'W': 'Week',
    'D': 'Day',
    'h': 'Hour',
    'm': 'Minute',
    's': 'Second'
}

# Map time units to pretty names -- shortened
TIME_KEYS_MAP_SHORT = {
    'Y': 'yr',
    'Q': 'qtr',
    'M': 'mnth',
    'W': 'wk',
    'D': 'day',
    'h': 'hr',
    'm': 'min',
    's': 'sec'
}

# Bucket dict
BUCKET_DICT = {
    1: ["0-50", "Small"],
    2: ["50-250", "Small"],
    3: ["250-500", "Small"],
    4: ["500-1K", "Medium"],
    5: ["1K-5K", "Medium"],
    6: ["5K-10K", "Medium"],
    7: ["10K-50K", "Large"],
    8: ["50K-100K", "Large"],
    9: ["100K-500K", "Large"],
    10: ["500K-1M", "Large"],
    11: ["1M-10M", "Very large"],
    12: ["10M-100M", "Very large"],
    13: ["100M-500M", "Very large"],
    14: ["500M-1B", "Very large"],
    15: ["1B+", "Very large"]
}
