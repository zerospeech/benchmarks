from typing import Tuple, List, Dict, ClassVar

import pandas as pd
from pydantic import Field

from .data_model import ABX17Submission
from ...datasets import ZRC2017Dataset
from ...tasks.abx.abx_librispeech import SimpleABXTask
from ....model import m_benchmark, m_data_items

return_type = List[Tuple[str, m_data_items.FileListItem, m_data_items.FileItem]]


class ABX17Task(SimpleABXTask):
    """ ABX task for abx-17 """

    def format_results(self, results: Dict) -> pd.DataFrame:
        results = [
            (dset.split('_')[0], dset.split('_')[1], mode, score)
            for dset, v in results.items() for mode, score in v.items()
        ]

        return pd.DataFrame(
            results, columns=['language', 'duration', 'type', 'score']
        )

    def extract_sets(self, submission: ABX17Submission, dataset: ZRC2017Dataset) -> return_type:
        self.sets = submission.sets
        self.tasks = submission.tasks
        abx_sets = []
        if 'english' in self.tasks:
            if '1s' in self.sets:
                abx_sets.append((
                    'english_1s',
                    dataset.index.subsets.english.items.abx_1s_item,
                    submission.items.english_1s
                ))
            if '10s' in self.sets:
                abx_sets.append((
                    'english_10s',
                    dataset.index.subsets.english.items.abx_10s_item,
                    submission.items.english_10s
                ))
            if '120s' in self.sets:
                abx_sets.append((
                    'english_120s',
                    dataset.index.subsets.english.items.abx_120s_item,
                    submission.items.english_120s
                ))
        if 'french' in self.tasks:
            if '1s' in self.sets:
                abx_sets.append((
                    'french_1s',
                    dataset.index.subsets.french.items.abx_1s_item,
                    submission.items.french_1s
                ))
            if '10s' in self.sets:
                abx_sets.append((
                    'french_10s',
                    dataset.index.subsets.french.items.abx_10s_item,
                    submission.items.french_10s
                ))
            if '120s' in self.sets:
                abx_sets.append((
                    'french_120s',
                    dataset.index.subsets.french.items.abx_120s_item,
                    submission.items.french_120s
                ))
        if 'mandarin' in self.tasks:
            if '1s' in self.sets:
                abx_sets.append((
                    'mandarin_1s',
                    dataset.index.subsets.mandarin.items.abx_1s_item,
                    submission.items.mandarin_1s
                ))
            if '10s' in self.sets:
                abx_sets.append((
                    'mandarin_10s',
                    dataset.index.subsets.mandarin.items.abx_10s_item,
                    submission.items.mandarin_10s
                ))
            if '120s' in self.sets:
                abx_sets.append((
                    'mandarin_120s',
                    dataset.index.subsets.mandarin.items.abx_120s_item,
                    submission.items.mandarin_120s
                ))
        if 'german' in self.tasks:
            if '1s' in self.sets:
                abx_sets.append((
                    'german_1s',
                    dataset.index.subsets.german.items.abx_1s_item,
                    submission.items.german_1s
                ))
            if '10s' in self.sets:
                abx_sets.append((
                    'german_10s',
                    dataset.index.subsets.german.items.abx_10s_item,
                    submission.items.german_10s
                ))
            if '120s' in self.sets:
                abx_sets.append((
                    'german_120s',
                    dataset.index.subsets.german.items.abx_120s_item,
                    submission.items.german_120s
                ))
        if 'wolof' in self.tasks:
            if '1s' in self.sets:
                abx_sets.append((
                    'wolof_1s',
                    dataset.index.subsets.wolof.items.abx_1s_item,
                    submission.items.wolof_1s
                ))
            if '10s' in self.sets:
                abx_sets.append((
                    'wolof_10s',
                    dataset.index.subsets.wolof.items.abx_10s_item,
                    submission.items.wolof_10s
                ))
            if '120s' in self.sets:
                abx_sets.append((
                    'wolof_120s',
                    dataset.index.subsets.wolof.items.abx_120s_item,
                    submission.items.wolof_120s
                ))
        return abx_sets


class ABX17Benchmark(m_benchmark.Benchmark):
    """abx-LS is a benchmark on acoustic Units using the ABX metric.

    This benchmark has 2 sub-tasks :

    - clean
    - other

    Each task has two subsets:  dev, test
    For ABX measuring we use this module : https://github.com/zerospeech/libri-light-abx
    """
    _name: ClassVar[str] = "abx17"
    _doc_url: ClassVar[str] = "https://zerospeech.com/tasks/task_1/tasks_goals/"
    dataset: ZRC2017Dataset = Field(default_factory=lambda: ZRC2017Dataset.load())

    def run(self, submission: ABX17Submission):
        """ Run abx-17 tasks """
        params = submission.params
        self.console.print(f'Running {self.name} benchmark on {submission.location.name}')

        # create output
        submission.score_dir.mkdir(exist_ok=True, parents=True)
        task = ABX17Task(**params.get_task())
        task.eval(submission, self.dataset)

        self.console.print(f'[green]:heavy_check_mark:[/green]Evaluation of benchmark completed successfully ')
        self.console.print(f"Scores can be found @ {submission.score_dir}")
