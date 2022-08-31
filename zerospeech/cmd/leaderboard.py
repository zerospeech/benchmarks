import argparse
import sys
from pathlib import Path

from .cli_lib import CMD
from ..benchmarks import BenchmarkList
from ..out import error_console, warning_console, console as std_console


class Leaderboard(CMD):
    """ Leaderboard manager subcommand """
    COMMAND = "leaderboard"
    NAMESPACE = ""

    def init_parser(self, parser: argparse.ArgumentParser):
        pass

    def run(self, argv: argparse.Namespace):
        self.console.print(
            f"Available Leaderboards: {','.join(f.value for f in BenchmarkList)}"
        )


class LeaderboardGenerate(CMD):
    """ Generate a leaderboard entry """
    COMMAND = "generate"
    NAMESPACE = "leaderboard"

    def init_parser(self, parser: argparse.ArgumentParser):
        parser.add_argument("name")
        parser.add_argument("submission_dir")
        parser.add_argument('score_dir')
        parser.add_argument('-o', '--output', help="Output file")

    def run(self, argv: argparse.Namespace):
        try:
            bench = BenchmarkList(argv.name)
        except ValueError:
            error_console.log(f"Specified benchmark ({argv.name}) does not exist !!!!")
            warning_console.log(f"Use one of the following : {','.join(b for b in BenchmarkList)}")
            sys.exit(1)

        submission_dir = Path(argv.submission_dir)
        if not submission_dir.is_dir():
            error_console.log(f'Given directory {submission_dir} does not exist !')
            sys.exit(1)

        score_dir = Path(argv.score_dir)
        if not score_dir.is_dir():
            error_console.log(f'Given directory {score_dir} does not exist !')
            sys.exit(1)

        std_console.print("=> Loading scores...", style="chartreuse3")
        submission = bench.submission.load(submission_dir)
        params = submission.params
        meta_file = submission.meta

        scores = bench.score_dir( # noqa: bad typing
            location=Path("abxLS-scores"),
            meta_file=meta_file,
            params=params
        )

        leaderboard = scores.build_leaderboard()

        as_json = leaderboard.json(indent=4)

        if argv.output:
            with Path(argv.output).open('w') as fp:
                fp.write(as_json)
        else:
            std_console.out(as_json)


class LeaderboardUpload(CMD):
    """ Upload a leaderboard entry to zerospeech.com """
    COMMAND = "upload"
    NAMESPACE = "leaderboard"

    def init_parser(self, parser: argparse.ArgumentParser):
        pass

    def run(self, argv: argparse.Namespace):
        std_console.print("Functionality not yet implemented !", style="bold orange_red1")
