import warnings
from pathlib import Path
from typing import List, Union, Callable, Any

from .base_validators import BASE_VALIDATOR_FN_TYPE
from ..data_loaders import load_dataframe, load_numpy_array, FileError
from ..model import data_items, m_benchmark

return_type = List[m_benchmark.ValidationResponse]
COMPLEX_VALIDATION_FN = Callable[[Any, List[BASE_VALIDATOR_FN_TYPE]], return_type]


def dataframe_check(
        item: data_items.FileItem,
        additional_checks: List[BASE_VALIDATOR_FN_TYPE], **kwargs
) -> return_type:
    """ Check validity & apply additional checks to a Dataframe fileItem """
    results = []

    if item.file_type not in data_items.FileTypes.dataframe_types():
        return [m_benchmark.ValidationError(f'file type {item.file_type} cannot be converted into a dataframe',
                                            data=item.file)]

    try:
        df = load_dataframe(item, **kwargs)
    except Exception as e:  # noqa: broad exception is on purpose
        return [m_benchmark.ValidationError(f'{e}', data=item.file)]

    results.append(m_benchmark.ValidationOK(f"File {item.file} is a valid dataframe !"))

    for fn in additional_checks:
        results.extend(fn(df))

    return results


def numpy_array_check(file_item: Union[data_items.FileItem, Path],
                      additional_checks: List[BASE_VALIDATOR_FN_TYPE]) -> return_type:
    """ Check validity & apply additional checks to a Numpy fileItem """
    warnings.filterwarnings("error")
    try:
        array = load_numpy_array(file_item)
    except (FileError, ValueError, UserWarning):
        return [m_benchmark.ValidationError(f'File does not contain a numpy array', data=file_item)]

    results = [m_benchmark.ValidationOK(f'File contains a numpy array !', data=file_item)]

    for fn in additional_checks:
        results.extend(fn(array))

    return results


def numpy_array_list_check(
    item: data_items.FileListItem, f_list_checks: List[BASE_VALIDATOR_FN_TYPE],
    additional_checks: List[BASE_VALIDATOR_FN_TYPE]
) -> return_type:
    """ Check validity & apply additional checks to a list of Numpy fileItems """
    results = []

    for fn in f_list_checks:
        r = fn(item)
        results.extend(r)

    for i in item.files_list:
        results.extend(numpy_array_check(i, additional_checks))

    return results
