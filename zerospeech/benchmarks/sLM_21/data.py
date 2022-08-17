import abc
from pathlib import Path
from typing import Tuple

from rich.console import Console

from ..generic import Submission, Task, ScoresDir
from ...data_items import FileItem, FileListItem, FileTypes, Item
from ...datasets import Dataset, DatasetsDir, Namespace, DatasetNotInstalledError, DatasetNotFoundError
from ...meta_file import MetaFile
from ...out import console


class SLM21Dataset(Dataset):
    """ Class interfacing usage of the sLM21 dataset"""

    @classmethod
    def load(cls, load_index: bool = True) -> "SLM21Dataset":
        """ Load """
        dataset = DatasetsDir.load().get("sLM21-dataset", cls)

        if dataset is None:
            raise DatasetNotFoundError(f"The sLM21-dataset does not exist")

        if not dataset.installed:
            raise DatasetNotInstalledError("The sLM21-dataset is not installed locally")

        if load_index:
            dataset.load_index()
            # convert all paths to absolute paths
            dataset.index.make_absolute()

        return dataset


class SLM21Submission(Submission):
    """ Submission for SLM21 Benchmark """
    sets: Tuple = ('dev', 'test')
    tasks: Tuple = ('lexical', 'syntactic', 'semantic')

    @classmethod
    def load(cls, path: Path, score_dir: Path = Path("scores"), *,
             tasks=('lexical', 'syntactic', 'semantic'),
             sets=('dev', 'test')):
        """ Load submission for sLM21 benchmark (filter by available tasks & sets) """
        items = dict()

        # include lexical task for each set
        if 'lexical' in tasks:
            lexical_dir = path / 'lexical'
            if 'dev' in sets:
                items['lexical_dev'] = FileItem.from_file(lexical_dir / "dev.txt")
            if 'test' in sets:
                items['lexical_test'] = FileItem.from_file(lexical_dir / "test.txt")

        # include semantic task for each set
        if 'semantic' in tasks:
            semantic_dir = path / 'semantic'
            if 'dev' in sets:
                items['semantic_dev_synthetic'] = FileListItem.from_dir(
                    semantic_dir / "dev/synthetic", f_types=[FileTypes.npy, FileTypes.txt]
                )
                items['semantic_dev_librispeech'] = FileListItem.from_dir(
                    semantic_dir / "dev/librispeech", f_types=[FileTypes.npy, FileTypes.txt]
                )
            if 'test' in sets:
                items['semantic_test_synthetic'] = FileListItem.from_dir(
                    semantic_dir / "test/synthetic", f_types=[FileTypes.npy, FileTypes.txt]
                )
                items['semantic_test_librispeech'] = FileListItem.from_dir(
                    semantic_dir / "test/librispeech", f_types=[FileTypes.npy, FileTypes.txt]
                )

        # include syntactic for each set
        if 'syntactic' in tasks:
            syntactic_dir = path / 'syntactic'
            if 'dev' in sets:
                items['syntactic_dev'] = FileItem.from_file(syntactic_dir / "dev.txt")
            if 'test' in sets:
                items['syntactic_test'] = FileItem.from_file(syntactic_dir / "test.txt")

        # Return submission object
        return cls(
            sets=sets,
            tasks=tasks,
            meta=MetaFile.from_file(path / 'meta.yaml'),
            location=path,
            items=Namespace[Item](store=items),
            score_dir=score_dir
        )

    # todo implement a check method for sLM21 submission
    def is_valid(self):
        pass

    def get_scores(self) -> ScoresDir:
        pass


class SLM21Task(Task, abc.ABC):
    """ Abstract sLM21 task """
    _console: Console = console

    class Config:
        arbitrary_types_allowed = True
