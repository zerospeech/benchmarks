from typing import Optional

from pydantic import Field

from .data import SLM21Dataset
from ..generic import Benchmark, TaskList, Submission
from ...datasets import Dataset


class SLM21TaskList(TaskList):
    pass


class SLM21Benchmark(Benchmark):
    _name = "sLM21"
    dataset: Dataset = Field(default_factory=lambda: SLM21Dataset.load())
    task_list: Optional[SLM21TaskList] = None

    def run(self, submission: Submission):
        pass

