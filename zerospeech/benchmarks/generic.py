import abc
from pathlib import Path
from typing import Optional

from pydantic import BaseModel, root_validator

from ..data_items import Item
from ..datasets import Dataset, Namespace
from ..meta_file import MetaFile


class InvalidSubmissionError(Exception):
    """ Error used to signal a non valid submission """
    pass


class Submission(BaseModel, abc.ABC):
    meta: MetaFile
    location: Path
    items: Optional[Namespace[Item]]

    @classmethod
    @abc.abstractmethod
    def load(cls, path: Path):
        pass

    @abc.abstractmethod
    def check(self):
        pass


class ScoreList(BaseModel):
    pass


class Task(BaseModel, abc.ABC):
    """ Abstract definition of a task """
    @property
    def name(self) -> str:
        return getattr(self, '_name')

    @root_validator(pre=True)
    def base_validation(cls, values):
        assert hasattr(cls, "_name"), f"A benchmark requires a name (add a _name attribute to the subclass {cls})"

        return values

    @abc.abstractmethod
    def eval(self, submission: Submission, dataset: Dataset, output_dir: Path):
        """ Evaluation method """
        pass


class TaskList(BaseModel, abc.ABC):
    pass


class Benchmark(BaseModel, abc.ABC):
    """ A Generic benchmark class """
    dataset: Dataset
    submission: Submission
    score_dir: Path
    task_list: TaskList
    scores: ScoreList

    @property
    def name(self) -> str:
        return getattr(self, '_name')

    @root_validator(pre=True)
    def base_validation(cls, values):
        assert hasattr(cls, "_name"), f"A benchmark requires a name (add a _name attribute to the subclass {cls})"

        return values


class BenchmarkTest(Benchmark):
    _name = "zrNamed"
