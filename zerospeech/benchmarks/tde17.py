from typing import Tuple, ClassVar, Type

from pydantic import Field

from zerospeech.datasets import ZRC2017Dataset
from zerospeech.generics import FileItem
from zerospeech.submissions import Submission
from zerospeech.submissions.tde17 import TDE17Submission
from zerospeech.tasks import tde
from ._model import Benchmark


class TDE17Task(tde.TDETask):
    tasks: Tuple = ('english', 'french', 'mandarin', 'german', 'wolof')

    def from_submission(self, submission: "TDE17Submission", lang: str) -> FileItem:
        """ Extract current input class file from submission """
        current_input_classes_file = submission.items.get(lang)
        if current_input_classes_file is None:
            raise ValueError(f'Language {lang} was not found in current submission : {submission.location}')

        return current_input_classes_file

    def load_gold(self, dataset: ZRC2017Dataset, lang: str):
        """ Load gold object for current language set """
        current_data = dataset.index.subsets.get(lang)
        if current_data is None:
            raise ValueError(f'Language {lang} was not found in {dataset.name}')

        # load gold files
        return tde.Gold(
            wrd_path=str(current_data.items.alignment_words.file),
            phn_path=str(current_data.items.alignment_phones.file)
        )


class TDE17Benchmark(Benchmark):
    """tde-17 is a benchmark on Spoken term Discovery / Word segmentation

    This benchmark has 5 sub-tasks (one for each language)
    - english
    - french
    - mandarin
    - german
    - wolof

    Each task has 3 subsets: 1s, 10s, 120s
    These subsets split the same amount of speech into different segments.
    - 1s has 1-second segments
    - 10s has 10-second segments
    - 120s has 120-second segments

    For the TDE eval we use this module : https://github.com/zerospeech/tdev2
    """
    _name: ClassVar[str] = "tde17"
    _doc_url: ClassVar[str] = "https://zerospeech.com/tasks/task_2/tasks_goals/"
    __submission_cls__: Type[Submission] = TDE17Submission
    dataset: "ZRC2017Dataset" = Field(default_factory=lambda: ZRC2017Dataset.load())

    def run(self, submission: "TDE17Submission"):
        """ Run TDE-17 tasks """
        params = submission.params
        self.console.print(f'Running {self.name} benchmark on {submission.location.name}')

        # create output dir
        submission.score_dir.mkdir(exist_ok=True, parents=True)
        task = TDE17Task.parse_obj(params.dict())
        task.eval(submission, self.dataset)

        self.console.print('[green]:heavy_check_mark:[/green]Evaluation of benchmark completed successfully ')
        self.console.print(f"Scores can be found @ {submission.score_dir}")
