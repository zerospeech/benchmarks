from pathlib import Path
from typing import Callable, Any, Union

import numpy
import numpy as np
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


def load_numpy_array(file_item: Union[FileItem, Path]) -> numpy.ndarray:
    if isinstance(file_item, Path):
        file_item = FileItem.from_file(file_item)

    if file_item.file_type == FileTypes.txt:
        return np.loadtxt(file_item.file)
    elif file_item.file_type == FileTypes.npy:
        return np.load(str(file_item.file))
