from pydantic import Field

from .data import SLM21Dataset
from ..generic import Benchmark, TaskList, ScoreList
from ...datasets import Dataset


class SLM21TaskList(TaskList):
    pass


class SLM21Benchmark(Benchmark):
    _name = "sLM21"
    dataset: Dataset = Field(default_factory=lambda: SLM21Dataset.load())
    task_list: SLM21TaskList = ...
    scores: ScoreList = ...
