from pathlib import Path
from typing import Callable, Any, Union, Protocol, Tuple, List
from zipfile import ZipFile

import numpy
import numpy as np
import pandas as pd

from .model import data_items

FileLoaderType = Callable[[data_items.FileItem], Any]


class FileError(Exception):
    """ Error while accessing file data """


def load_dataframe(file_item: Union[data_items.FileItem, Path], **extras) -> pd.DataFrame:
    """ Open a column based file as dataframe """
    if isinstance(file_item, Path):
        file_item = data_items.FileItem.from_file(file_item)

    if not file_item.file.is_file():
        raise FileNotFoundError(f'File :{file_item.file} does not exist')

    if file_item.file_type not in data_items.FileTypes.dataframe_types():
        raise FileError(f"current type {file_item.file_type} cannot be converted to Dataframe")

    # open as dataframe
    return pd.read_csv(file_item.file, **extras)


def load_numpy_array(file_item: Union[data_items.FileItem, Path]) -> numpy.ndarray:
    if isinstance(file_item, Path):
        file_item = data_items.FileItem.from_file(file_item)

    if file_item.file_type not in data_items.FileTypes.numpy_types():
        raise FileError(f"current type {file_item.file_type} cannot be converted to a numpy array")

    if file_item.file_type == data_items.FileTypes.txt:
        return np.loadtxt(file_item.file)
    elif file_item.file_type == data_items.FileTypes.npy:
        return np.load(str(file_item.file))


class Zippable(Protocol):
    def __zippable__(self) -> List[Tuple[str, Path]]:
        pass


def zip_zippable(item: Zippable, archive_file: Path = Path("archive.zip")):
    """ Create a zip archive from an item that uses the Zippable protocol"""
    items_list = item.__zippable__()
    with ZipFile(archive_file, 'w') as zip_obj:
        for dir_name, filename in items_list:
            zip_obj.write(filename, f"{dir_name}{filename.name}")
