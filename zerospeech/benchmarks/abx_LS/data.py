from typing import Optional

from ...datasets import Dataset, DatasetsDir


class ABXLSDataset(Dataset):
    """ Class interfacing usage of the sLM21 dataset"""

    @classmethod
    def load(cls, load_index: bool = True) -> Optional["ABXLSDataset"]:
        """ Load """
        dataset = DatasetsDir.load().get("abxLS-dataset", cls=cls)
        if dataset and load_index:
            dataset.load_index()

        # convert all paths to absolute paths
        dataset.index.make_absolute()
        return dataset
