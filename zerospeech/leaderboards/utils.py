import json
from pathlib import Path
from typing import Optional
from urllib.error import HTTPError
from urllib.request import urlopen


def clean_label(label: str) -> str:
    return label.replace('<i>', '').replace('</i>', '') \
        .replace('<b>', '').replace('</b>', '')


def format_score(score: Optional[float], *, percent: bool = True) -> str:

    if score is None:
        return "-"

    if percent:
        return f"{(score * 100):.2f}%"
    else:
        return f"{score:.5f}"


def open_json(target: str):
    """ Opens a json either locally or via the internet """
    p = Path(target)
    if p.is_file():
        with p.open() as fp:
            return json.load(fp)

    # target is url
    try:
        response = urlopen(target)
        return json.loads(response.read())
    except ValueError:
        raise ValueError(f'Target {target} appears to be nor a file nor a url')
    except HTTPError as e:
        raise ValueError(f'Target {target} is a url but returned {e.code}')
