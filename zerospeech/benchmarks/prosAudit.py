from typing import ClassVar, Type

from pydantic import Field

from zerospeech.datasets import ProsAuditLMDataset
from zerospeech.submissions import Submission
from zerospeech.submissions.prosAudit import ProsodySubmission
from zerospeech.tasks.lm import ProsodicTask
from ._model import Benchmark


class SLMProsodyBenchmark(Benchmark):
    """ sLMProsody is a benchmark on spoken language Modeling

    This benchmark evaluates speech on a prosodic level (todo: expand description a bit)
    """
    _name: ClassVar[str] = "prosAudit"
    _doc_url: ClassVar[str] = "https://zerospeech.com/tasks/task_4/tasks_goals/#prosody"
    __submission_cls__: Type[Submission] = ProsodySubmission
    dataset: ProsAuditLMDataset = Field(default_factory=lambda: ProsAuditLMDataset.load())

    def run(self, submission: "ProsodySubmission"):
        """ Run sLMProsody benchmark """
        params = submission.params
        self.console.print(f'Running {self.name} benchmark on {submission.location.name}')

        # create output dir
        submission.score_dir.mkdir(exist_ok=True, parents=True)
        task = ProsodicTask(**params.dict())
        task.eval(submission, self.dataset)

        self.console.print('[green]:heavy_check_mark:[/green]Evaluation of benchmark completed successfully ')
        self.console.print(f"Scores can be found @ {submission.score_dir}")
