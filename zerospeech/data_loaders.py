from typing import Callable, Any

import pandas as pd

from .data_items import FileTypes, FileItem

FileLoaderType = Callable[[FileItem], Any]


class FileError(Exception):
    """ Error while accessing file data """


def load_dataframe(file: FileItem, **extras) -> pd.DataFrame:
    """ Open a column based file as dataframe """
    allowed_types = (FileTypes.csv, FileTypes.txt, FileTypes.tsv)
    if file.file_type not in allowed_types:
        raise FileError(f"current type {file.file_type} cannot be converted to Dataframe")

    # open as dataframe
    return pd.read_csv(file.file, **extras)
