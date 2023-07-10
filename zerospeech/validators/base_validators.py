from pathlib import Path
from typing import List, Callable, Any, Type

import numpy as np
import pandas as pd

from zerospeech.generics import FileListItem
from zerospeech.submissions import ValidationResponse, ValidationOK, ValidationError

# Type for base functions
BASE_VALIDATOR_FN_TYPE = Callable[[Any], List[ValidationResponse]]
return_type = List[ValidationResponse]


def list_checker(given: List[str], expected: List[str]) -> return_type:
    """ Check a list of strings to find if expected items are in it """
    given = set(given)
    expected = set(expected)

    if given != expected:
        has_less_files = expected - given
        has_more_files = given - expected
        res = []

        if len(has_more_files) > 0:

            for e_file in has_more_files:
                res.append(
                    ValidationError(
                        "extra file found",
                        filename=e_file
                    )
                )
        elif len(has_less_files) > 0:
            res = []
            for e_file in has_less_files:
                res.append(ValidationError(
                    "expected file not found",
                    filename=e_file
                ))

        return res
    else:
        return [ValidationOK('expected files found')]


def file_list_checker(
        item: FileListItem, expected: List[Path]
) -> return_type:
    """ Check if a file list has expected files in it """
    file_names = [f.stem for f in item.files_list]
    expected_names = [f.stem for f in expected]
    return list_checker(given=file_names, expected=expected_names)


def dataframe_column_check(df: pd.DataFrame, expected_columns: List[str]) -> return_type:
    """ Check that all columns are present in a dataframe """
    columns = list(df.columns)
    if columns != expected_columns:
        return [ValidationError(f'columns are not expected '
                                            f'expected: {expected_columns}, found: {columns}')]

    return [ValidationOK('Columns of dataframe are valid')]


def dataframe_index_check(df: pd.DataFrame, expected: List[str]) -> return_type:
    """ Check that specific values are contained in each row"""
    # check if all files from the dataset are represented in the filenames
    index = list(df.index)
    return list_checker(index, expected)


def dataframe_type_check(df: pd.DataFrame, col_name: str, expected_type: Type[Any]) -> return_type:
    """ Verify column type matches expected type """
    try:
        df[col_name].astype(expected_type)
    except ValueError:
        return [ValidationError(f'Column {col_name} does not march expected type {expected_type}')]
    return []


def numpy_dimensions_check(array: np.ndarray, ndim: int):
    """ Check ndarray matches specified dimensions"""
    if array.ndim != ndim:
        return [ValidationError(
            f'Array should be of dimensions: {ndim}')]
    return []


def numpy_dtype_check(array: np.ndarray, dtype: np.dtype):
    """ Check ndarray matches specified type """
    if array.dtype != dtype:
        return [ValidationError(
            f'Array should be of type: {dtype}')]
    return []


def numpy_col_comparison(dim: int):
    ncols = []

    def comparison(array: np.ndarray):
        ncols.append(array.shape[dim])

        if len(set(ncols)) != 1:
            return [
                ValidationError(f'Arrays do not match dimensions {dim}')
            ]
        return []

    return comparison
