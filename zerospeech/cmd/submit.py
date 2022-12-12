import argparse
import sys
from pathlib import Path

from .cli_lib import CMD
from ..benchmarks import BenchmarkList
from ..model import m_meta_file
from ..out import error_console, warning_console, console as std_console


class SubmitOnline(CMD):
    """ Submit your results to zerospeech.com """
    COMMAND = "submit"
    NAMESPACE = ""

    def init_parser(self, parser: argparse.ArgumentParser):
        pass

    def generate_leaderboard(self, bench, submission_dir):
        if not submission_dir.is_dir():
            error_console.log(f'Given directory {submission_dir} does not exist !')
            sys.exit(1)

        submission = bench.submission.load(submission_dir)
        if not submission.score_dir.is_dir():
            error_console.log(f'Given directory {submission.score_dir} does not exist !')
            sys.exit(1)
        std_console.print("=> Loading scores...", style="chartreuse3")

        params = submission.params
        meta_file = submission.meta
        scores = bench.score_dir( # noqa: bad typing
            location=Path("abxLS-scores"),
            meta_file=meta_file,
            params=params
        )

        leaderboard = scores.build_leaderboard()

        as_json = leaderboard.json(indent=4)
        # todo: write into submission

    @staticmethod
    def get_benchmark(submission_dir: Path):
        if not submission_dir.is_dir():
            error_console(f"Location specified does not exist !!!")
            sys.exit(2)

        benchmark_name = None
        try:
            benchmark_name = m_meta_file.MetaFile.benchmark_from_submission(submission_dir)
            if benchmark_name is None:
                raise TypeError("benchmark not found")

            return BenchmarkList(benchmark_name)
        except TypeError:
            error_console.log(f"Specified submission does not have a valid {m_meta_file.MetaFile.file_stem}"
                              f"\nCannot find benchmark type")
            sys.exit(1)
        except ValueError:
            error_console.log(f"Specified benchmark ({benchmark_name}) does not exist !!!!")
            warning_console.log(f"Use one of the following : {','.join(b for b in BenchmarkList)}")
            sys.exit(1)

    def run(self, argv: argparse.Namespace):
        # todo: actions that need to be performed
        # 0) if current user is not logged in prompt for login
        # 1) load submission
        # 2) verify all components are valid
        #   a) source files
        #   b) score files
        #   c) meta.yaml (with required entries)
        #   d) params.yaml
        # 3) generate leaderboard.json
        # 4) create/verify model_id
        # 5) zip all files
        # 6) upload
        warning_console.print("The submit functionality is a work in progress")
        warning_console.print("It will be available in January 2023 !!!")
