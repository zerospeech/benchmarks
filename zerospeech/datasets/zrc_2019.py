import functools
from typing import Optional

from ._model import Dataset, DatasetNotFoundError, DatasetsDir, DatasetNotInstalledError


class ZRC2019Dataset(Dataset):
    """ Class interfacing usage of the ZRC 2019 test dataset """

    @classmethod
    @functools.lru_cache
    def load(cls, load_index: bool = True) -> Optional["ZRC2019Dataset"]:
        """ Loads the dataset """
        dataset = DatasetsDir.load().get("zrc2019-dataset", cls=cls)

        if dataset is None:
            raise DatasetNotFoundError("The zrc2019-dataset does not exist")

        if not dataset.installed:
            raise DatasetNotInstalledError("The zrc2019-dataset is not installed locally")

        if load_index:
            dataset.load_index()
            # convert all paths to absolute paths
            dataset.index.make_absolute()

        return dataset
