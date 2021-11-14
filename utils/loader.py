import json

import yaml
from yaml.loader import SafeLoader


def read_yaml(path: str) -> dict:
    with open(path) as f:
        return yaml.load(f, Loader=SafeLoader)


def read_json(path: str) -> dict:
    with open(path) as f:
        return json.load(f)
