from .data import SLM21Task
from ..generic import Submission
from ...datasets import Dataset


# todo implement semantic task
class SemanticTask(SLM21Task):
    _name = "semantic"

    def eval(self, submission: Submission, dataset: Dataset):
        pass
