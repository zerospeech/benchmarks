from pathlib import Path

from .data import SLM21Task
from ..generic import Submission
from ...datasets import Dataset


# todo implement syntactic task
class SyntacticTask(SLM21Task):
    _name = "syntactic"

    def eval(self, submission: Submission, dataset: Dataset, output_dir: Path):
        pass
