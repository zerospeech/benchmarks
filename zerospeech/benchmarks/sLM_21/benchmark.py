from pydantic import Field

from .submission import SLM21Submission
from .dataset import SLM21Dataset
from .lexical import LexicalTask
from .semantic import SemanticTask
from .syntactic import SyntacticTask
from ...model import m_benchmark


class SLM21Benchmark(m_benchmark.Benchmark):
    """sLM21 is a benchmark on spoken Language Modeling.

    This benchmark has 3 sub-tasks :

    - Lexical Task
    - Syntactic Task
    - Semantic Task

    Each task has two subsets:  dev, test

    For more information visit: https://version2.zerospeech.com/tasks/task_4/tasks_goals/
    """
    _name = "sLM21"
    dataset: SLM21Dataset = Field(default_factory=lambda: SLM21Dataset.load())

    def run(self, submission: SLM21Submission):
        """ Run sLM21 tasks """
        params = submission.params

        # create output dir
        submission.score_dir.mkdir(exist_ok=True, parents=True)
        if 'lexical' in submission.tasks:
            task1 = LexicalTask(**params.get_lexical())
            task1.eval(submission, self.dataset)

        if 'semantic' in submission.tasks:
            task2 = SemanticTask(**params.get_semantic())
            task2.eval(submission, self.dataset)

        if 'syntactic' in submission.tasks:
            task3 = SyntacticTask(**params.get_syntactic())
            task3.eval(submission, self.dataset)

        # todo leaderboard entry ...
