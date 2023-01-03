from typing import Tuple, List, Dict, ClassVar

import pandas
import pandas as pd
from pydantic import Field

from .data_model import AbxLSRobSubmission
from ...datasets import AbxLSDataset
from ...tasks.abx_phoneme import SimpleABXPhonemeTask, ContextMode
from ....model import m_benchmark, m_data_items

return_type = List[Tuple[str, m_data_items.FileListItem, m_data_items.FileItem]]


class AbxLSRobTask(SimpleABXPhonemeTask):
    """ ABX task for abx-LS-Rob """

    def format_results(self, results: Dict) -> pd.DataFrame:
        return pandas.DataFrame(results)

    def extract_sets(
            self, submission: AbxLSRobSubmission,
            dataset: AbxLSDataset, context: ContextMode = ContextMode.all) -> return_type:
        """ Extract relevant data for abx from submission & dataset """
        self.sets = submission.sets
        self.tasks = submission.tasks
        abx_sets = []
        if ContextMode.within in context.as_set():
            item_type = "phoneme_item_file"
            if 'dev' in self.sets:
                if 'clean' in self.tasks:
                    abx_sets.append((
                        'dev-clean-phoneme',
                        dataset.index.subsets.dev_clean.items.get(item_type),
                        submission.items.dev_clean
                    ))
                if 'other' in self.tasks:
                    abx_sets.append((
                        'dev-other-phoneme',
                        dataset.index.subsets.dev_other.items.get(item_type),
                        submission.items.dev_other,
                    ))

            if 'test' in self.sets:
                if 'clean' in self.tasks:
                    abx_sets.append((
                        'test-clean-phoneme',
                        dataset.index.subsets.test_clean.items.get(item_type),
                        submission.items.test_clean,
                    ))
                if 'other' in self.tasks:
                    abx_sets.append((
                        'test-other-phoneme',
                        dataset.index.subsets.test_other.items.get(item_type),
                        submission.items.test_other,
                    ))

            if ContextMode.any in context.as_set():
                item_type = "triphone_item_file"
                if 'dev' in self.sets:
                    if 'clean' in self.tasks:
                        abx_sets.append((
                            'dev-clean-triphone',
                            dataset.index.subsets.dev_clean.items.get(item_type),
                            submission.items.dev_clean
                        ))
                    if 'other' in self.tasks:
                        abx_sets.append((
                            'dev-other-triphone',
                            dataset.index.subsets.dev_other.items.get(item_type),
                            submission.items.dev_other,
                        ))

                if 'test' in self.sets:
                    if 'clean' in self.tasks:
                        abx_sets.append((
                            'test-clean-triphone',
                            dataset.index.subsets.test_clean.items.get(item_type),
                            submission.items.test_clean,
                        ))
                    if 'other' in self.tasks:
                        abx_sets.append((
                            'test-other-triphone',
                            dataset.index.subsets.test_other.items.get(item_type),
                            submission.items.test_other,
                        ))

            return abx_sets


class AbxLSRobBenchmark(m_benchmark.Benchmark):
    """ abx-LS-Phoneme is a benchmark on acoustic Units using the ABX metric.

    It is a reimplementation of the ABX-LS benchmark with more robust .item files


    This benchmark has 2 sub-tasks :

    - clean
    - other

    Each task has two subsets:  dev, test
    For ABX measuring we use this module : https://github.com/zerospeech/libri-light-abx2
    """
    _name: ClassVar[str] = "abxLSPhon"
    _doc_url: ClassVar[str] = "https://zerospeech.com/tasks/task_1/tasks_goals/"
    dataset: AbxLSDataset = Field(default_factory=lambda: AbxLSDataset.load())

    def run(self, submission: AbxLSRobSubmission):
        """ run ABX-LSRob tasks """
        params = submission.params
        self.console.print(f'Running {self.name} benchmark on {submission.location.name}')
        # create output dir
        submission.score_dir.mkdir(exist_ok=True, parents=True)
        task = AbxLSRobTask(**params.get_task())
        task.eval(submission, self.dataset)

        self.console.print(f'[green]:heavy_check_mark:[/green]Evaluation of benchmark completed successfully ')
        self.console.print(f"Scores can be found @ {submission.score_dir}")
