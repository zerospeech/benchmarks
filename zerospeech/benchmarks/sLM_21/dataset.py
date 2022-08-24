import functools

from ...model import m_datasets


class SLM21Dataset(m_datasets.Dataset):
    """ Class interfacing usage of the sLM21 dataset"""

    @classmethod
    @functools.lru_cache
    def load(cls, load_index: bool = True) -> "SLM21Dataset":
        """ Load dataset from dir registry """
        dataset = m_datasets.DatasetsDir.load().get("sLM21-dataset", cls)

        if dataset is None:
            raise m_datasets.DatasetNotFoundError(f"The sLM21-dataset does not exist")

        if not dataset.installed:
            raise m_datasets.DatasetNotInstalledError("The sLM21-dataset is not installed locally")

        if load_index:
            dataset.load_index()
            # convert all paths to absolute paths
            dataset.index.make_absolute()

        return dataset
