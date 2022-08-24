import functools
from typing import Optional

from ...model import m_datasets


class AbxLSDataset(m_datasets.Dataset):
    """ Class interfacing usage of the ABX-LS dataset"""

    @classmethod
    @functools.lru_cache
    def load(cls, load_index: bool = True) -> Optional["AbxLSDataset"]:
        """ Load """
        dataset = m_datasets.DatasetsDir.load().get("abxLS-dataset", cls=cls)

        if dataset is None:
            raise m_datasets.DatasetNotFoundError(f"The abxLS-dataset does not exist")

        if not dataset.installed:
            raise m_datasets.DatasetNotInstalledError("The abxLS-dataset is not installed locally")

        if load_index:
            dataset.load_index()
            # convert all paths to absolute paths
            dataset.index.make_absolute()

        return dataset