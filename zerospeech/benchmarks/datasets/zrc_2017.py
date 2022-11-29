import functools
from typing import Optional, ClassVar

from ...model import m_datasets


class ZRC2017Dataset(m_datasets.Dataset):
    """ Class interfacing usage of the ZRC 2017 test dataset """
    __dataset_name__: ClassVar[str] = "zrc2017-test-dataset"

    @classmethod
    @functools.lru_cache
    def load(cls, load_index: bool = True) -> Optional["ZRC2017Dataset"]:
        """ Loads the dataset """
        dataset = m_datasets.DatasetsDir.load().get(cls.__dataset_name__, cls=cls)

        if dataset is None:
            raise m_datasets.DatasetNotFoundError(f"The zrc2017-test-dataset does not exist")

        if not dataset.installed:
            raise m_datasets.DatasetNotInstalledError("The zrc2017-test-dataset is not installed locally")

        if load_index:
            dataset.load_index()
            # convert all paths to absolute paths
            dataset.index.make_absolute()

        return dataset
