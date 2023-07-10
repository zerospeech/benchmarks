import argparse
import functools
import itertools
import sys
from io import StringIO
from pathlib import Path
from typing import Optional, List, Tuple, Dict

import pandas as pd
from rich.console import Console

from zerospeech.leaderboards.sLM21 import SLM21Leaderboard, SLM21LeaderboardEntry
from zerospeech.leaderboards.utils import open_json, clean_label, format_score
from .base import LeaderboardExporter, CSVExporter

console = Console()
void_console = Console(file=StringIO())


def restrict_entry(e: SLM21LeaderboardEntry, percent: bool = True) -> Tuple[Dict, Dict]:
    _format_score = functools.partial(format_score, percent=percent)
    base_info = dict(
        label=clean_label(e.publication.author_short),
        model_id=e.model_id,
        submission_di=e.submission_id
    )

    dev_set = dict(
        **base_info,
        set="dev",
        lexical_all=_format_score(e.scores.lexical.all.dev),
        lexical_in_vocab=_format_score(e.scores.lexical.in_vocab.dev),
        syntactic=_format_score(e.scores.syntactic.dev),
        semantic_synth=e.scores.semantic.normal.synthetic.dev,
        semantic_libri=e.scores.semantic.normal.librispeech.dev,
        semantic_w_synth=e.scores.semantic.weighted.synthetic.dev,
        semantic_w_libri=e.scores.semantic.weighted.librispeech.dev
    )

    test_set = dict(
        **base_info,
        set="test",
        lexical_all=_format_score(e.scores.lexical.all.test),
        lexical_in_vocab=_format_score(e.scores.lexical.in_vocab.test),
        syntactic=_format_score(e.scores.syntactic.test),
        semantic_synth=e.scores.semantic.normal.synthetic.test,
        semantic_libri=e.scores.semantic.normal.librispeech.test,
        semantic_w_synth=e.scores.semantic.weighted.synthetic.test,
        semantic_w_libri=e.scores.semantic.weighted.librispeech.test
    )

    return dev_set, test_set


class Slm21Exporter(LeaderboardExporter, CSVExporter):
    leaderboard: SLM21Leaderboard
    # split dev & test set
    split_sets: bool = True
    # keep values as percentage
    as_percentage: bool = True
    quiet: bool = False

    @property
    def console(self):
        if not self.quiet:
            return console
        return void_console

    def restricted_entries(self):
        return [
            restrict_entry(e)
            for e in self.leaderboard.data
        ]

    @classmethod
    def from_cmd(cls, argv: Optional[List[str]] = None):
        argv = argv if argv is not None else sys.argv[1:]
        parser = argparse.ArgumentParser("ABXLS leaderboard to CSV")
        parser.add_argument('location', help='Location of leaderboard (url/path)')
        parser.add_argument('-s', '--split-sets', action='store_true', help="Split dev and test")
        parser.add_argument('-p', '--as-percentage', action='store_true', help="Scores are shown as percentages")
        parser.add_argument('-q', '--quiet', action='store_true')
        parser.add_argument('-o', '--output-file', default="slm21.csv", help="File to output results")
        args = parser.parse_args(argv)
        if not args.quiet:
            console.print("Loading...", style="bold orange3")

        ld_data = open_json(args.location)
        return cls(
            leaderboard=ld_data,
            split_sets=args.split_sets,
            as_percentage=args.as_percentage,
            quiet=args.quiet,
            output_file=Path(args.output_file)
        )

    def to_csv(self):
        entries_restricted = self.restricted_entries()
        dev_restricted, test_restricted = zip(*entries_restricted)

        if not self.split_sets:
            all_restricted = [
                x for x in itertools.chain.from_iterable(
                    itertools.zip_longest(dev_restricted, test_restricted)
                )
                if x
            ]

            self.console.print(f"Writing {self.output_file}...")
            df_all = pd.DataFrame(all_restricted)
            df_all.to_csv(self.output_file)
        else:
            dev_file = self.output_file.parent / f"dev_{self.output_file.name}"
            self.console.print(f"Writing {dev_file}...")
            df_dev = pd.DataFrame(dev_restricted)
            del df_dev['set']
            df_dev.to_csv(dev_file)

            test_file = self.output_file.parent / f"test_{self.output_file.name}"

            self.console.print(f"Writing {test_file}...")
            df_test = pd.DataFrame(test_restricted)
            del df_test['set']
            df_test.to_csv(test_file)


def cmd():
    """ Command line entrypoint """
    exp = Slm21Exporter.from_cmd()
    exp.export()
    exp.console.print("Leaderboard exported successfully", style="bold green")
