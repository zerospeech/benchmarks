import argparse
import sys
from pathlib import Path

from ..benchmarks import BenchmarkList
from .cli_lib import CMD
from ..out import error_console, console, warning_console


class BenchmarksCMD(CMD):
    """ List available benchmarks """
    COMMAND = "benchmarks"
    NAMESPACE = ""

    def init_parser(self, parser: argparse.ArgumentParser):
        pass

    def run(self, argv: argparse.Namespace):
        console.print(
            f"Available Benchmarks: {','.join(f.value for f in BenchmarkList)}"
        )


class BenchmarkRunCMD(CMD):
    """ Run a benchmark """
    COMMAND = "run"
    NAMESPACE = "benchmarks"

    def init_parser(self, parser: argparse.ArgumentParser):
        parser.add_argument("name")
        parser.add_argument("submission_dir")
        parser.add_argument("-o", "--output", default="scores", help="Output location")
        parser.add_argument("-s", "--sets", nargs='*', action='store', default=('all',),
                            help="Limit the sets the benchmark is run on")
        parser.add_argument("-t", "--tasks", nargs='*', action='store', default=('all',),
                            help="Limit the tasks the benchmark runs")
        parser.add_argument('-q', '--quiet', action='store_true', default=False,
                            help="Do not print information to stdout")

    def run(self, argv: argparse.Namespace):
        try:
            bench = BenchmarkList(argv.name)
        except ValueError:
            error_console.log(f"Specified benchmark ({argv.name}) does not exist !!!!")
            warning_console.log(f"Use one of the following : {','.join(b for b in BenchmarkList)}")
            sys.exit(1)

        sub_dir = Path(argv.submission_dir)
        if not sub_dir.is_dir():
            error_console.log(f"Submission directory given does not exist !!!")
            sys.exit(1)

        submission = bench.submission.load(path=sub_dir)
        # todo check validity of submission

        if 'all' not in argv.sets:
            submission.sets = argv.sets

        if 'all' not in argv.tasks:
            submission.tasks = argv.tasks

        # load saved parameters
        submission.params = submission.load_parameters()

        # update values from args
        submission.params.quiet = argv.quiet

        # Load & run benchmark
        benchmark = bench.benchmark()
        benchmark.run(submission)


class BenchmarkParamsCMD(CMD):
    """ Create template params.yaml """
    COMMAND = "params"
    NAMESPACE = "benchmarks"

    def init_parser(self, parser: argparse.ArgumentParser):
        parser.add_argument("name")
        parser.add_argument("submission_dir")

    def run(self, argv: argparse.Namespace):
        try:
            bench = BenchmarkList(argv.name)
        except ValueError:
            error_console.log(f"Specified benchmark ({argv.name}) does not exist !!!!")
            warning_console.log(f"Use one of the following : {','.join(b for b in BenchmarkList)}")
            sys.exit(1)

        sub_dir = Path(argv.submission_dir)
        if not sub_dir.is_dir():
            error_console.log(f"Submission directory given does not exist !!!")
            sys.exit(1)

        # remove old params file if exists
        (sub_dir / bench.parameters.file_stem).unlink(missing_ok=True)

        submission = bench.submission.load(path=sub_dir)
        console.log(f"Params file created/reset at @ {submission.params_file}")


class BenchmarksInfoCMD(CMD):
    """ List information on a benchmark """
    COMMAND = "info"
    NAMESPACE = "benchmarks"

    def init_parser(self, parser: argparse.ArgumentParser):
        parser.add_argument("name")

    def run(self, argv: argparse.Namespace):
        try:
            bench = BenchmarkList(argv.name)
        except ValueError:
            error_console.log(f"Specified benchmark ({argv.name}) does not exist !!!!")
            warning_console.log(f"Use one of the following : {','.join(b for b in BenchmarkList)}")
            sys.exit(1)

        # print benchmark documentation
        console.print(bench.benchmark.__doc__)
