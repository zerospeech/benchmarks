from typing import Tuple, List, Dict, ClassVar

import pandas
import pandas as pd
from pydantic import Field

from .data_model import AbxLSSubmission
from ...datasets import AbxLSDataset
from ...tasks.abx.abx_phoneme import SimpleABXPhonemeTask, ContextMode
from ....model import m_benchmark, m_data_items

return_type = Tuple[str, m_data_items.FileItem, m_data_items.FileListItem, ContextMode]


class AbxLSTask(SimpleABXPhonemeTask):
    """ ABX task for abx-LS-Rob """

    def format_results(self, results: Dict) -> pd.DataFrame:
        formatted_results = []

        for key, lst in results.items():
            for obj in lst:
                formatted_results.append(
                    dict(
                        subset='-'.join(key.split('-')[:2]),
                        speaker_mode=obj.get("abx-s-condition"),
                        context_mode=obj.get('abx-c-condition'),
                        granularity=obj.get('dataset'),
                        score=obj.get('score'),
                        # item_file=Path(obj.get('item-file')).name,
                        pooling=obj.get('pooling'),
                        seed=obj.get('seed'),
                    )
                )

        return pandas.DataFrame(formatted_results)

    def extract_sets(
            self, submission: AbxLSSubmission,
            dataset: AbxLSDataset, context: ContextMode = ContextMode.all) -> List[return_type]:
        """ Extract relevant data for abx from submission & dataset """
        self.sets = submission.sets
        self.tasks = submission.tasks
        abx_sets = []

        if ContextMode.triphone_within in context.as_set():
            item_type = "triphone_item_file"
            if 'dev' in self.sets:
                if 'clean' in self.tasks:
                    abx_sets.append((
                        'dev-clean-triphone-within',
                        dataset.index.subsets.dev_clean.items.get(item_type),
                        submission.items.dev_clean,
                        context.triphone_within
                    ))
                if 'other' in self.tasks:
                    abx_sets.append((
                        'dev-other-triphone-within',
                        dataset.index.subsets.dev_other.items.get(item_type),
                        submission.items.dev_other,
                        context.triphone_within
                    ))

            if 'test' in self.sets:
                if 'clean' in self.tasks:
                    abx_sets.append((
                        'test-clean-triphone-within',
                        dataset.index.subsets.test_clean.items.get(item_type),
                        submission.items.test_clean,
                        context.triphone_within
                    ))
                if 'other' in self.tasks:
                    abx_sets.append((
                        'test-other-triphone-within',
                        dataset.index.subsets.test_other.items.get(item_type),
                        submission.items.test_other,
                        context.triphone_within
                    ))

            if ContextMode.phoneme_within in context.as_set():
                item_type = "phoneme_item_file"
                if 'dev' in self.sets:
                    if 'clean' in self.tasks:
                        abx_sets.append((
                            'dev-clean-phoneme-within',
                            dataset.index.subsets.dev_clean.items.get(item_type),
                            submission.items.dev_clean,
                            context.phoneme_within
                        ))
                    if 'other' in self.tasks:
                        abx_sets.append((
                            'dev-other-phoneme-within',
                            dataset.index.subsets.dev_other.items.get(item_type),
                            submission.items.dev_other,
                            context.phoneme_within
                        ))

                if 'test' in self.sets:
                    if 'clean' in self.tasks:
                        abx_sets.append((
                            'test-clean-phoneme-within',
                            dataset.index.subsets.test_clean.items.get(item_type),
                            submission.items.test_clean,
                            context.phoneme_within
                        ))
                    if 'other' in self.tasks:
                        abx_sets.append((
                            'test-other-phoneme-within',
                            dataset.index.subsets.test_other.items.get(item_type),
                            submission.items.test_other,
                            context.phoneme_within
                        ))

                if ContextMode.phoneme_any in context.as_set():
                    item_type = "phoneme_item_file"
                    if 'dev' in self.sets:
                        if 'clean' in self.tasks:
                            abx_sets.append((
                                'dev-clean-phoneme-any',
                                dataset.index.subsets.dev_clean.items.get(item_type),
                                submission.items.dev_clean,
                                context.phoneme_any
                            ))
                        if 'other' in self.tasks:
                            abx_sets.append((
                                'dev-other-phoneme-any',
                                dataset.index.subsets.dev_other.items.get(item_type),
                                submission.items.dev_other,
                                context.phoneme_any
                            ))

                    if 'test' in self.sets:
                        if 'clean' in self.tasks:
                            abx_sets.append((
                                'test-clean-phoneme-any',
                                dataset.index.subsets.test_clean.items.get(item_type),
                                submission.items.test_clean,
                                context.phoneme_any
                            ))
                        if 'other' in self.tasks:
                            abx_sets.append((
                                'test-other-phoneme-any',
                                dataset.index.subsets.test_other.items.get(item_type),
                                submission.items.test_other,
                                context.phoneme_any
                            ))

            return abx_sets


class AbxLSBenchmark(m_benchmark.Benchmark):
    """ abx-LS-Phoneme is a benchmark on acoustic Units using the ABX metric.

    It is a reimplementation of the ABX-LS benchmark with more robust .item files


    This benchmark has 2 sub-tasks :

    - clean
    - other

    Each task has two subsets:  dev, test
    For ABX measuring we use this module : https://github.com/zerospeech/libri-light-abx2
    """
    _name: ClassVar[str] = "abxLS"
    _doc_url: ClassVar[str] = "https://zerospeech.com/tasks/task_1/tasks_goals/"
    dataset: AbxLSDataset = Field(default_factory=lambda: AbxLSDataset.load())

    def run(self, submission: AbxLSSubmission):
        """ run ABX-LSRob tasks """
        params = submission.params
        self.console.print(f'Running {self.name} benchmark on {submission.location.name}')
        # create output dir
        submission.score_dir.mkdir(exist_ok=True, parents=True)
        task = AbxLSTask(**params.get_task())
        task.eval(submission, self.dataset)

        self.console.print(f'[green]:heavy_check_mark:[/green]Evaluation of benchmark completed successfully ')
        self.console.print(f"Scores can be found @ {submission.score_dir}")
