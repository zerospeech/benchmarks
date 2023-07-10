import functools
from typing import Optional, ClassVar

from ._model import Dataset, DatasetNotFoundError, DatasetsDir, DatasetNotInstalledError


class SLM21Dataset(Dataset):
    """ Class interfacing usage of the sLM21 dataset"""
    __dataset_name__: ClassVar[str] = "sLM21-dataset"

    @classmethod
    @functools.lru_cache
    def load(cls, load_index: bool = True) -> Optional["SLM21Dataset"]:
        """ Load dataset from dir registry """
        dataset = DatasetsDir.load().get(cls.__dataset_name__, cls)

        if dataset is None:
            raise DatasetNotFoundError("The sLM21-dataset does not exist")

        if not dataset.installed:
            raise DatasetNotInstalledError("The sLM21-dataset is not installed locally")

        if load_index:
            dataset.load_index()
            # convert all paths to absolute paths
            dataset.index.make_absolute()

        return dataset


class AbxLSDataset(Dataset):
    """ Class interfacing usage of the ABX-LS dataset"""
    __dataset_name__: ClassVar[str] = "abxLS-dataset"

    @classmethod
    @functools.lru_cache
    def load(cls, load_index: bool = True) -> Optional["AbxLSDataset"]:
        """ Load """
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


class ProsAuditLMDataset(Dataset):
    """ Class interfacing usage of the Prosody LM Benchmark """
    __dataset_name__: ClassVar[str] = "prosaudit-dataset"

    @classmethod
    @functools.lru_cache
    def load(cls, load_index: bool = True) -> Optional["ProsAuditLMDataset"]:
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
