import abc
import json
import os
import signal
import sys
import warnings
from typing import Tuple, Set, TYPE_CHECKING

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

from zerospeech.misc import exit_after
from zerospeech.generics import FileItem
from zerospeech.tasks import Task

if TYPE_CHECKING:
    from zerospeech.datasets import Dataset
    from zerospeech.submissions import Submission


class TDETask(Task, abc.ABC):
    """ TDE Task """
    _name = "tde-task"
    tasks: Tuple
    metrics: Set = {'grouping', 'matching', 'boundary', 'token_type', 'nlp'}
    n_jobs: int = 1
    result_filename: str = "scores.json"
    grouping_max_time: int = 7200

    @staticmethod
    def read_discovered(item: FileItem, gold: Gold):
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
            with self.console.status(f"Computing {lang} boundary"):
                boundary = Boundary(gold, discovered)
                boundary.compute_boundary()
                scores['boundary'].update(dict(
                    precision=boundary.precision,
                    recall=boundary.recall,
                    fscore=boundary.fscore
                ))
            self.console.print(f"Boundary computed for {lang} :heavy_check_mark:", style="bold green")

        # Token & Type
        if 'token_type' in self.metrics:
            with self.console.status(f"Computing {lang} token & type"):
                token_type = TokenType(gold, discovered)
                token_type.compute_token_type()
                scores['token'] = dict()
                scores['type'] = dict()
                scores['token']['precision'], scores['type']['precision'] = token_type.precision
                scores['token']['recall'], scores['type']['recall'] = token_type.recall
                scores['token']['fscore'], scores['type']['fscore'] = token_type.fscore
                scores['nlp']['nwords'] = len(token_type.type_seen),
            self.console.print(f"Token & Type computed for {lang} :heavy_check_mark:", style="bold green")

        # NLP
        if 'nlp' in self.metrics:
            with self.console.status(f"Computing {lang} NLP"):
                coverage = Coverage(gold, discovered)
                coverage.compute_coverage()
                ned = Ned(discovered)
                ned.compute_ned()
                scores["nlp"].update(dict(
                    ned=ned.ned,
                    coverage=coverage.coverage,
                    npairs=ned.n_pairs
                ))
            self.console.print(f"NLP computed for {lang} :heavy_check_mark:", style="bold green")

        # Grouping
        if 'grouping' in self.metrics:

            @exit_after(self.grouping_max_time)
            def compute_grouping():
                """ Compute grouping within allocated time """
                with self.console.status(f"Computing {lang} Grouping"):
                    grouping = Grouping(discovered)
                    grouping.compute_grouping()
                    return dict(
                        precision=grouping.precision,
                        recall=grouping.recall,
                        fscore=grouping.fscore
                    )

            try:
                grouping_score = compute_grouping()
                scores['grouping'].update(grouping_score)
                self.console.print(f"Grouping computed for {lang} :heavy_check_mark:", style="bold green")
            except KeyboardInterrupt:
                scores['grouping'].update(dict(
                    precision=None,
                    recall=None,
                    fscore=None
                ))
                self.console.print(f"Grouping computing for {lang} was aborted due to timeout !!", style="bold red")

        def score_or_none(data):
            if len(data):
                return data
            return None

        return {m: score_or_none(score) for m, score in scores.items()}

    @abc.abstractmethod
    def from_submission(self, submission: "Submission", lang: str) -> FileItem:
        """ Extract current input class file from submission """
        pass

    @abc.abstractmethod
    def load_gold(self, dataset: "Dataset", lang: str) -> Gold:
        """ Load gold object for current language set """
        pass

    def _eval_lang(self, submission: "Submission", dataset: "Dataset", lang: str):
        """ Evaluate tde for specific language """
        current_input_classes_file = self.from_submission(submission, lang)
        self.console.print(f"Loading gold for {lang}...")
        gold = self.load_gold(dataset, lang)

        # load discovered intervals
        self.console.print(f"Loading class discovery for {lang}...")
        discovered = self.read_discovered(
            current_input_classes_file, gold
        )

        # return results
        self.console.print(f"Gathering metrics for {lang} ...")
        return lang, self.gather_metrics(gold, discovered, lang)

    def eval(self, submission: "Submission", dataset: "Dataset"):
        """ Evaluate the submission """

        # Run evaluation with multiprocess if specified
        res = joblib.Parallel(n_jobs=self.n_jobs)(
            joblib.delayed(self._eval_lang)(submission, dataset, lang) for lang in self.tasks
        )
        scores = dict(res)
        self.console.print(f":pencil: writing scores {self.result_filename}", style="underline yellow4")
        with (submission.score_dir / self.result_filename).open('w') as fp:
            json.dump(scores, fp)
