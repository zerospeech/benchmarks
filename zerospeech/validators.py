from pathlib import Path
from typing import List, Optional, Tuple

import pandas as pd

from .model import data_items, m_benchmark
from .data_loaders import load_dataframe


def list_checker(given: List[str], expected: List[str]):
    """ Check a list of strings to find if expected items are in it """
    given = set(given)
    expected = set(expected)

    if given != expected:
        has_less_files = expected - given
        has_more_files = given - expected

        if len(has_more_files) > 0:
            return [m_benchmark.ValidationError(
                "more files found",
                data=has_more_files
            )]

        if len(has_less_files) > 0:
            return [m_benchmark.ValidationError(
                "missing files",
                data=has_less_files
            )]
    else:
        return [m_benchmark.ValidationOK('expected files found')]


def file_list_checker(item: data_items.FileListItem, expected: List[Path]) -> List[m_benchmark.ValidationResponse]:
    """ Check if a file list has expected files in it """
    file_names = [f.stem for f in item.files_list]
    expected_names = [f.stem for f in expected]
    return list_checker(file_names, expected_names)


return_type = Tuple[List[m_benchmark.ValidationResponse], Optional[pd.DataFrame]]


def dataframe_check(item: data_items.FileItem, expected_columns: Optional[List[str]] = None, **kwargs) -> return_type:
    if item.file_type not in data_items.FileTypes.dataframe_types():
        return [m_benchmark.ValidationError(f'file type {item.file_type} cannot be converted into a dataframe',
                                            data=item.file)], None

    try:
        df = load_dataframe(item, **kwargs)
    except Exception as e:  # noqa: broad exception is on purpose
        return [m_benchmark.ValidationError(f'{e}', data=item.file)], None

    columns = list(df.columns)

    if columns != expected_columns:
        return [m_benchmark.ValidationError(f'columns are not expected '
                                            f'expected: {expected_columns}, found: {columns}')], None

    return [m_benchmark.ValidationOK('dataframe validates tests')], df
