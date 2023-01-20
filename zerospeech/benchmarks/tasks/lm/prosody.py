from typing import TYPE_CHECKING

from .params import ProsodyLMParameters
from ....model import m_benchmark

if TYPE_CHECKING:
    from ..._benchmarks.sLM_prosody import SLMProsodySubmission
    from ...datasets import ProsodyLMDataset

default_params = ProsodyLMParameters()


class ProsodicTask(m_benchmark.Task):
    """ Allows computation of the score for the prosodic task (todo: write better desc)"""
    _name = "prosodic"
    sets = ('dev', 'test')
    tasks = ('english', 'french', 'japanese')
    result_filename: str = default_params.results_filename

    def eval(self, submission: "SLMProsodySubmission", dataset: "ProsodyLMDataset"):
        """ Evaluate prosody for the given submission """
        output_dir = submission.score_dir
        self.sets = submission.sets
        self.tasks = submission.tasks

        result = dict()
        if 'dev' in self.sets:
            if 'english' in self.tasks:
                pass
            if 'french' in self.tasks:
                pass
            if 'japanese' in self.tasks:
                pass

        if 'test' in self.sets:
            if 'english' in self.tasks:
                pass
            if 'french' in self.tasks:
                pass
            if 'japanese' in self.tasks:
                pass
