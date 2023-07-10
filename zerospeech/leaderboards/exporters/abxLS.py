import argparse
import functools
import itertools
import json
import sys
from io import StringIO
from pathlib import Path
from typing import Dict, Tuple, List, Optional

import pandas as pd
from rich.console import Console

from zerospeech.leaderboards.abxLS import ABXLSLeaderboard
from zerospeech.leaderboards.utils import open_json, clean_label, format_score
from .base import CSVExporter, LeaderboardExporter

console = Console()
void_console = Console(file=StringIO())


def restrict_entry(entry: Dict, percent: bool = True) -> Tuple[Dict, Dict]:
    _format_score = functools.partial(format_score, percent=percent)
    pub_info = entry.get('publication', {})
    base_info = dict(
        label=clean_label(pub_info.get('author_short', '-')),
        model_id=entry.get('model_id', '-'),
        submission_id=entry.get('submission_id', '-'),
    )
    score = entry.get('scores', {})
    dev_set = dict(
        **base_info,
        set="dev",
        # phoneme any
        # clean
        phoneme_any_clean_within=_format_score(score['phoneme']['any']['clean']['within']['dev']['score']),
        phoneme_any_clean_across=_format_score(score['phoneme']['any']['clean']['across']['dev']['score']),
        # other
        phoneme_any_other_within=_format_score(score['phoneme']['any']['other']['within']['dev']['score']),
        phoneme_any_other_across=_format_score(score['phoneme']['any']['other']['across']['dev']['score']),
        # phoneme within
        # clean
        phoneme_within_clean_within=_format_score(score['phoneme']['within']['clean']['within']['dev']['score']),
        phoneme_within_clean_across=_format_score(score['phoneme']['within']['clean']['across']['dev']['score']),
        # other
        phoneme_within_other_within=_format_score(score['phoneme']['within']['other']['within']['dev']['score']),
        phoneme_within_other_across=_format_score(score['phoneme']['within']['other']['across']['dev']['score']),
        # triphone within
        # clean
        triphone_within_clean_within=_format_score(score['triphone']['within']['clean']['within']['dev']['score']),
        triphone_within_clean_across=_format_score(score['triphone']['within']['clean']['across']['dev']['score']),
        # other
        triphone_within_other_within=_format_score(score['triphone']['within']['other']['within']['dev']['score']),
        triphone_within_other_across=_format_score(score['triphone']['within']['other']['across']['dev']['score']),
    )

    test_set = dict(
        **base_info,
        set="test",
        # phoneme any
        # clean
        phoneme_any_clean_within=_format_score(score['phoneme']['any']['clean']['within']['test']['score']),
        phoneme_any_clean_across=_format_score(score['phoneme']['any']['clean']['across']['test']['score']),
        # other
        phoneme_any_other_within=_format_score(score['phoneme']['any']['other']['within']['test']['score']),
        phoneme_any_other_across=_format_score(score['phoneme']['any']['other']['across']['test']['score']),
        # phoneme within
        # clean
        phoneme_within_clean_within=_format_score(score['phoneme']['within']['clean']['within']['test']['score']),
        phoneme_within_clean_across=_format_score(score['phoneme']['within']['clean']['across']['test']['score']),
        # other
        phoneme_within_other_within=_format_score(score['phoneme']['within']['other']['within']['test']['score']),
        phoneme_within_other_across=_format_score(score['phoneme']['within']['other']['across']['test']['score']),
        # triphone within
        # clean
        triphone_within_clean_within=_format_score(score['triphone']['within']['clean']['within']['test']['score']),
        triphone_within_clean_across=_format_score(score['triphone']['within']['clean']['across']['test']['score']),
        # other
        triphone_within_other_within=_format_score(score['triphone']['within']['other']['within']['test']['score']),
        triphone_within_other_across=_format_score(score['triphone']['within']['other']['across']['test']['score']),
    )
    return dev_set, test_set


class ABXLSExporter(LeaderboardExporter, CSVExporter):
    leaderboard: ABXLSLeaderboard
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

    @classmethod
    def from_cmd(cls, argv: Optional[List[str]] = None):
        argv = argv if argv is not None else sys.argv[1:]
        parser = argparse.ArgumentParser("ABXLS leaderboard to CSV")
        parser.add_argument('location', help='Location of leaderboard (url/path)')
        parser.add_argument('-s', '--split-sets', action='store_true', help="Split dev and test")
        parser.add_argument('-p', '--as-percentage', action='store_true', help="Scores are shown as percentages")
        parser.add_argument('-q', '--quiet', action='store_true')
        parser.add_argument('-o', '--output-file', default="abx-ls.csv", help="File to output results")
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

    def restricted_entries(self) -> List[Tuple[Dict, Dict]]:
        # passthrough json to serialise all values
        as_dict = json.loads(self.leaderboard.json())
        return [
            restrict_entry(e, percent=self.as_percentage) for e in as_dict["data"]
        ]

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
    exp = ABXLSExporter.from_cmd()
    exp.export()
    exp.console.print("Leaderboard exported successfully", style="bold green")
