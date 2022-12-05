from typing import Tuple, List, Dict, ClassVar

import pandas as pd
from pydantic import Field

from .data_model import AbxLSSubmission
from ...datasets import AbxLSDataset
from ...tasks.abx_librispech import SimpleABXTask
from ....model import m_benchmark, m_data_items

return_type = List[Tuple[str, m_data_items.FileListItem, m_data_items.FileItem]]


class AbxLSTask(SimpleABXTask):
    """ Abx task for abx-LS """

    def format_results(self, results: Dict) -> pd.DataFrame:
        """ Format the results as a dataframe """
        results = [
            (dset.split('-')[0], dset.split('-')[1], mode, score)
            for dset, v in results.items() for mode, score in v.items()
        ]
        return pd.DataFrame(
            results, columns=['dataset', 'sub-dataset', 'type', 'score']
        )

    def extract_sets(self, submission: AbxLSSubmission, dataset: AbxLSDataset) -> return_type:
        """ Extract relevant data for abx from submission & dataset """
        self.sets = submission.sets
        self.tasks = submission.tasks
        abx_sets = []
        if 'dev' in self.sets:
            if 'clean' in self.tasks:
                abx_sets.append((
                    'dev-clean',
                    dataset.index.subsets.dev_clean.items.item_file,
                    submission.items.dev_clean
                ))
            if 'other' in self.tasks:
                abx_sets.append((
                    'dev-other',
                    dataset.index.subsets.dev_other.items.item_file,
                    submission.items.dev_other,
                ))

        if 'test' in self.sets:
            if 'clean' in self.tasks:
                abx_sets.append((
                    'test-clean',
                    dataset.index.subsets.test_clean.items.item_file,
                    submission.items.test_clean,
                ))
            if 'other' in self.tasks:
                abx_sets.append((
                    'test-other',
                    dataset.index.subsets.test_other.items.item_file,
                    submission.items.test_other,
                ))
        return abx_sets


class AbxLSBenchmark(m_benchmark.Benchmark):
    """abx-LS is a benchmark on acoustic Units using the ABX metric.

    This benchmark has 2 sub-tasks :

    - clean
    - other

    Each task has two subsets:  dev, test
    For ABX measuring we use this module : https://github.com/zerospeech/libri-light-abx
    """
    _name: ClassVar[str] = "abxLS"
    _doc_url: ClassVar[str] = "https://zerospeech.com/tasks/task_1/tasks_goals/"
    dataset: AbxLSDataset = Field(default_factory=lambda: AbxLSDataset.load())

    def run(self, submission: AbxLSSubmission):
        """ Run abx-LS tasks """
        params = submission.params
        self.console.print(f'Running {self.name} benchmark on {submission.location.name}')

        # create output dir
        submission.score_dir.mkdir(exist_ok=True, parents=True)
        task = AbxLSTask(**params.get_task())
        task.eval(submission, self.dataset)

        self.console.print(f'[green]:heavy_check_mark:[/green]Evaluation of benchmark completed successfully ')
        self.console.print(f"Scores can be found @ {submission.score_dir}")
