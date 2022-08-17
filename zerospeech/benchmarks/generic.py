import abc
from pathlib import Path
from typing import Optional

from pydantic import BaseModel, root_validator

from ..data_items import Item
from ..datasets import Dataset, Namespace
from ..meta_file import MetaFile
from ..out import console as out_console, void_console


class InvalidSubmissionError(Exception):
    """ Error used to signal a non valid submission """
    pass


class ScoresDir(BaseModel):
    pass


class Submission(BaseModel, abc.ABC):
    meta: MetaFile
    location: Path
    items: Optional[Namespace[Item]]
    score_dir: Path = Path('scores')

    @classmethod
    @abc.abstractmethod
    def load(cls, path: Path, score_dir: Path = Path("scores"), **kwargs):
        pass

    @abc.abstractmethod
    def is_valid(self):
        pass

    @abc.abstractmethod
    def get_scores(self) -> ScoresDir:
        """ Load scores """
        pass


class Task(BaseModel, abc.ABC):
    """ Abstract definition of a task """
    quiet: bool = False

    @property
    def name(self) -> str:
        return getattr(self, '_name')

    @property
    def console(self):
        """ Console to print output """
        if self.quiet:
            return void_console
        return out_console

    @root_validator(pre=True)
    def base_validation(cls, values):
        assert hasattr(cls, "_name"), f"A benchmark requires a name (add a _name attribute to the subclass {cls})"

        return values

    @abc.abstractmethod
    def eval(self, submission: Submission, dataset: Dataset):
        """ Evaluation method """
        pass


class TaskList(BaseModel, abc.ABC):
    # todo method to configure tasklist from a big set of params
    pass


class Benchmark(BaseModel, abc.ABC):
    """ A Generic benchmark class """
    dataset: Dataset
    task_list: TaskList

    @property
    def name(self) -> str:
        return getattr(self, '_name')

    @root_validator(pre=True)
    def base_validation(cls, values):
        assert hasattr(cls, "_name"), f"A benchmark requires a name (add a _name attribute to the subclass {cls})"
        return values

    @abc.abstractmethod
    def run(self, submission: Submission):
        """ Run the benchmark """
        pass

