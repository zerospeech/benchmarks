import abc
import json
import os
import signal
import sys
from typing import Tuple, Set
import warnings

import joblib

try:
    from tde.measures.boundary import Boundary
    from tde.measures.coverage import Coverage
    from tde.measures.grouping import Grouping
    from tde.measures.ned import Ned
    from tde.measures.token_type import TokenType
    from tde.readers.disc_reader import Disc
    from tde.readers.gold_reader import Gold
except ImportError:
    Boundary, Coverage, Grouping, Ned = ..., ..., ..., ...
    TokenType, Disc, Gold = ..., ..., ...
    warnings.warn('tde module was not installed')

from ...model import m_benchmark, m_data_items


class TDETask(m_benchmark.Task, abc.ABC):
    """ TDE Task """
    _name = "tde-task"
    tasks: Tuple
    metrics: Set = {'grouping', 'matching', 'boundary', 'token_type', 'nlp'}
    n_jobs: int = 1
    result_filename: str = "scores.json"
    grouping_max_time: int = 7200

    @staticmethod
    def read_discovered(item: m_data_items.FileItem, gold: Gold):
        """ Load discovered Intervals """
        # Disc class prints a bunch of nonsense, so we force it to be quiet
        sys.stdout = open(os.devnull, 'w')
        try:
            return Disc(str(item.file), gold)
        finally:
            sys.stdout = sys.__stdout__

    def gather_metrics(self, gold: Gold, discovered: Disc, lang: str):
        scores = dict(
            matching=dict(), boundary=dict(), token=dict(), type=dict(), nlp=dict(), grouping=dict()
        )

        # Boundary
        if 'boundary' in self.metrics:
            self.console.status(f"Computing {lang} boundary")
            boundary = Boundary(gold, discovered)
            boundary.compute_boundary()
            scores['boundary'].update(dict(
                precision=boundary.precision,
                recall=boundary.recall,
                fscore=boundary.fscore
            ))
            self.console.print(f"Boundary computed :heavy_check_mark:", style="bold green")

        # Token & Type
        if 'token_type' in self.metrics:
            self.console.status(f"Computing {lang} token & type")
            token_type = TokenType(gold, discovered)
            token_type.compute_token_type()
            scores['token'] = dict()
            scores['type'] = dict()
            scores['token']['precision'], scores['type']['precision'] = token_type.precision
            scores['token']['recall'], scores['type']['recall'] = token_type.recall
            scores['token']['fscore'], scores['type']['fscore'] = token_type.fscore
            scores['nlp']['nwords'] = len(token_type.type_seen),
            self.console.print(f"Token & Type computed :heavy_check_mark:", style="bold green")

        # NLP
        if 'nlp' in self.metrics:
            self.console.status(f"Computing {lang} NLP")
            coverage = Coverage(gold, discovered)
            coverage.compute_coverage()
            ned = Ned(discovered)
            ned.compute_ned()
            scores["nlp"].update(dict(
                ned=ned.ned,
                coverage=coverage.coverage,
                npairs=ned.n_pairs
            ))

        # Grouping
        if 'grouping' in self.metrics:
            self.console.status(f"Computing {lang} Grouping")

            def handler(signum, frame): # noqa: needs to follow signature
                self.console.print(f'==> Grouping of {lang} takes too long, skipping..', style='red bold')
                raise TimeoutError('timeout')

            # todo: investigate why a timeout is needed ?
            # todo investigate if a better way exists to add a timeout
            signal.signal(signal.SIGALRM, handler)
            signal.alarm(self.grouping_max_time)

            try:
                grouping = Grouping(discovered)
                grouping.compute_grouping()
                scores['grouping'].update(dict(
                    precision=grouping.precision,
                    recall=grouping.recall,
                    fscore=grouping.fscore
                ))
            except TimeoutError:
                scores['grouping'].update(dict(
                    precision=None,
                    recall=None,
                    fscore=None
                ))

        def score_or_none(data):
            if len(data):
                return data
            return None

        return {m: score_or_none(score) for m, score in scores.items()}

    @abc.abstractmethod
    def from_submission(self, submission: m_benchmark.Submission, lang: str) -> m_data_items.FileItem:
        """ Extract current input class file from submission """
        pass

    @abc.abstractmethod
    def load_gold(self, dataset: m_benchmark.Dataset, lang: str) -> Gold:
        """ Load gold object for current language set """
        pass

    def _eval_lang(self, submission: m_benchmark.Submission, dataset: m_benchmark.Dataset, lang: str):
        """ Evaluate tde for specific language """
        current_input_classes_file = self.from_submission(submission, lang)
        gold = self.load_gold(dataset, lang)

        # load discovered intervals
        discovered = self.read_discovered(
            current_input_classes_file, gold
        )

        # return results
        return lang, self.gather_metrics(gold, discovered, lang)

    def eval(self, submission: m_benchmark.Submission, dataset: m_benchmark.Dataset):
        """ Evaluate the submission """

        # Run evaluation with multiprocess if specified
        res = joblib.Parallel(n_jobs=self.n_jobs)(
            joblib.delayed(self._eval_lang)(self, submission, dataset, lang) for lang in self.tasks
        )
        scores = dict(res)
        self.console.print(f":pencil: writing {self.result_filename}", style="underline yellow4")
        with (submission.score_dir / self.result_filename).open('w') as fp:
            json.dump(scores, fp)
