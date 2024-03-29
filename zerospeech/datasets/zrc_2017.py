import functools
from typing import Optional, ClassVar

from ._model import Dataset, DatasetNotFoundError, DatasetsDir, DatasetNotInstalledError


class ZRC2017Dataset(Dataset):
    """ Class interfacing usage of the ZRC 2017 test dataset """
    __dataset_name__: ClassVar[str] = "zrc2017-test-dataset"

    @classmethod
    @functools.lru_cache
    def load(cls, load_index: bool = True) -> Optional["ZRC2017Dataset"]:
        """ Loads the dataset """
        dataset = DatasetsDir.load().get(cls.__dataset_name__, cls=cls)

        if dataset is None:
            raise DatasetNotFoundError(f"The {cls.__dataset_name__} does not exist")

        if not dataset.installed:
            raise DatasetNotInstalledError(f"The {cls.__dataset_name__} is not installed locally")

        if load_index:
            dataset.load_index()
            # convert all paths to absolute paths
            dataset.index.make_absolute()

        return dataset
