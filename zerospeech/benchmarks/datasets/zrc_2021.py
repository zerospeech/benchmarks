import functools
from typing import Optional, ClassVar

from ...model import m_datasets


class SLM21Dataset(m_datasets.Dataset):
    """ Class interfacing usage of the sLM21 dataset"""
    __dataset_name__: ClassVar[str] = "sLM21-dataset"

    @classmethod
    @functools.lru_cache
    def load(cls, load_index: bool = True) -> Optional["SLM21Dataset"]:
        """ Load dataset from dir registry """
        dataset = m_datasets.DatasetsDir.load().get(cls.__dataset_name__, cls)

        if dataset is None:
            raise m_datasets.DatasetNotFoundError(f"The sLM21-dataset does not exist")

        if not dataset.installed:
            raise m_datasets.DatasetNotInstalledError("The sLM21-dataset is not installed locally")

        if load_index:
            dataset.load_index()
            # convert all paths to absolute paths
            dataset.index.make_absolute()

        return dataset


class AbxLSDataset(m_datasets.Dataset):
    """ Class interfacing usage of the ABX-LS dataset"""
    __dataset_name__: ClassVar[str] = "abxLS-dataset"

    @classmethod
    @functools.lru_cache
    def load(cls, load_index: bool = True) -> Optional["AbxLSDataset"]:
        """ Load """
        dataset = m_datasets.DatasetsDir.load().get(cls.__dataset_name__, cls=cls)

        if dataset is None:
            raise m_datasets.DatasetNotFoundError(f"The abxLS-dataset does not exist")

        if not dataset.installed:
            raise m_datasets.DatasetNotInstalledError("The abxLS-dataset is not installed locally")

        if load_index:
            dataset.load_index()
            # convert all paths to absolute paths
            dataset.index.make_absolute()

        return dataset
