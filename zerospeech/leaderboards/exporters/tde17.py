import argparse
import functools
import sys
from io import StringIO
from pathlib import Path
from typing import Optional, List, Dict

import pandas as pd
from rich.console import Console

from zerospeech.leaderboards.tde17 import TDE17Leaderboard, TDE17Entry
from zerospeech.leaderboards.utils import open_json, clean_label, format_score
from .base import LeaderboardExporter, CSVExporter

console = Console()
void_console = Console(file=StringIO())


def restrict_entry(e: TDE17Entry) -> Dict:
    _format_score = functools.partial(format_score, percent=False)
    return dict(
        label=clean_label(e.publication.author_short),
        model_id=e.model_id,
        submission_di=e.submission_id,
        # EN
        en_ned=_format_score(e.scores.english.nlp.ned),
        en_cov=_format_score(e.scores.english.nlp.coverage),
        en_wrds=e.scores.english.nlp.nwords,
        # FR
        fr_ned=_format_score(e.scores.french.nlp.ned),
        fr_cov=_format_score(e.scores.french.nlp.coverage),
        fr_wrds=e.scores.french.nlp.nwords,
        # Mandarin
        cmn_ned=_format_score(e.scores.mandarin.nlp.ned),
        cmn_cov=_format_score(e.scores.mandarin.nlp.coverage),
        cmn_wrds=e.scores.mandarin.nlp.nwords,
        # Wolof
        wol_ned=_format_score(e.scores.wolof.nlp.ned),
        wol_cov=_format_score(e.scores.wolof.nlp.coverage),
        wol_wrds=e.scores.wolof.nlp.nwords,
    )


class TDE17Exporter(LeaderboardExporter, CSVExporter):
    leaderboard: TDE17Leaderboard
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
        parser.add_argument('-q', '--quiet', action='store_true')
        parser.add_argument('-o', '--output-file', default="tde17.csv", help="File to output results")
        args = parser.parse_args(argv)
        if not args.quiet:
            console.print("Loading...", style="bold orange3")

        ld_data = open_json(args.location)
        # return ld_data

        return cls(
            leaderboard=ld_data,
            quiet=args.quiet,
            output_file=Path(args.output_file)
        )

    def to_csv(self):
        df = pd.DataFrame(self.restricted_entries())
        self.console.print(f"Writing {self.output_file}...")
        df.to_csv(self.output_file)


def cmd():
    """ Command line entrypoint """
    exp = TDE17Exporter.from_cmd()

    # for entry in exp['data']:
    #     try:
    #         _ = TDE17Entry.parse_obj(entry)
    #     except ValidationError as e:
    #         print(f"failed with: {entry['model_id']}")

    exp.export()
    exp.console.print("Leaderboard exported successfully", style="bold green")
