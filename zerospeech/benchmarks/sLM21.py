from typing import ClassVar, TYPE_CHECKING

from pydantic import Field

from zerospeech.datasets import SLM21Dataset
from zerospeech.tasks.lm import LexicalTask, SyntacticTask, SemanticTask
from ._model import Benchmark

if TYPE_CHECKING:
    from zerospeech.submissions.sLM21 import SLM21Submission


class SLM21Benchmark(Benchmark):
    """sLM21 is a benchmark on spoken Language Modeling.

    This benchmark has 3 sub-tasks :

    - Lexical Task
    - Syntactic Task
    - Semantic Task

    Each task has two subsets:  dev, test
    """
    _name: ClassVar[str] = "sLM21"
    _doc_url: ClassVar[str] = "https://zerospeech.com/tasks/task_4/tasks_goals/"
    dataset: SLM21Dataset = Field(default_factory=lambda: SLM21Dataset.load())

    def run(self, submission: "SLM21Submission"):
        """ Run sLM21 tasks """
        params = submission.params
        self.console.print(f'Running {self.name} benchmark on {submission.location.name}')

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

        self.console.print('[green]:heavy_check_mark:[/green]Evaluation of benchmark completed successfully ')
        self.console.print(f"Scores can be found @ {submission.score_dir}")
