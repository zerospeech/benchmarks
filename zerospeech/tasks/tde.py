import abc
import json
import os
import sys
import warnings
from pathlib import Path
from typing import Tuple, Set, TYPE_CHECKING, NamedTuple

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


class TDEItems(NamedTuple):
    wrd_path: Path
    phn_path: Path
    input_classes: Path


class TDETask(Task, abc.ABC):
    """ TDE Task """
    _name = "tde-task"
    tasks: Tuple
    metrics: Set = {'grouping', 'matching', 'boundary', 'token_type', 'nlp'}
    njobs: int = 1
    result_filename: str = "scores.json"
    grouping_max_time: int = 7200

    @staticmethod
    def read_discovered(item: Path, gold: Gold):
        """ Load discovered Intervals """
        # Disc class prints a bunch of nonsense, so we force it to be quiet
        sys.stdout = open(os.devnull, 'w')
        try:
            return Disc(str(item), gold)
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

    @staticmethod
    def load_gold(wrd: Path, phn: Path) -> Gold:
        """ Load gold object for current language set """
        # load gold files
        return Gold(
            wrd_path=str(wrd),
            phn_path=str(phn)
        )

    def _eval_lang(self, lang: str, items: TDEItems):
        """ Evaluate tde for specific language """
        self.console.print(f"Loading gold for {lang}...")
        gold = self.load_gold(wrd=items.wrd_path, phn=items.phn_path)

        # load discovered intervals
        self.console.print(f"Loading class discovery for {lang}...")
        discovered = self.read_discovered(
            items.input_classes, gold
        )

        self.console.print(f"Gathering metrics for {lang} ...")
        return lang, self.gather_metrics(gold, discovered, lang)

    @abc.abstractmethod
    def gather_items(self, lang: str, submission: "Submission", dataset: "Dataset") -> TDEItems:
        pass

    def eval(self, submission: "Submission", dataset: "Dataset"):
        """ Evaluate the submission """
        print(f"Running with {self.njobs} cores!!")
        # Run evaluation with multiprocess if specified
        eval_items = {
            lang: self.gather_items(lang=lang, submission=submission, dataset=dataset)
            for lang in self.tasks
        }

        res = joblib.Parallel(n_jobs=self.njobs)(
            joblib.delayed(self._eval_lang)(lang, items) for lang, items in eval_items.items()
        )
        scores = dict(res)
        self.console.print(f":pencil: writing scores {self.result_filename}", style="underline yellow4")
        with (submission.score_dir / self.result_filename).open('w') as fp:
            json.dump(scores, fp)
