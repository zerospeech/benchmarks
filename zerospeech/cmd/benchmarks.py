import argparse
import sys
from pathlib import Path

from .cli_lib import CMD
from ..benchmarks import BenchmarkList
from ..model import m_benchmark
from ..out import error_console, warning_console


class BenchmarksCMD(CMD):
    """ List available benchmarks """
    COMMAND = "benchmarks"
    NAMESPACE = ""

    def init_parser(self, parser: argparse.ArgumentParser):
        pass

    def run(self, argv: argparse.Namespace):
        self.console.print(
            f"Available Benchmarks: {','.join(f.value for f in BenchmarkList)}"
        )


class BenchmarkRunCMD(CMD):
    """ Run a benchmark """
    COMMAND = "run"
    NAMESPACE = "benchmarks"

    def init_parser(self, parser: argparse.ArgumentParser):
        parser.add_argument("name")
        parser.add_argument("submission_dir")
        parser.add_argument("-o", "--output", default="scores", help="Output location"),
        parser.add_argument('--skip-validation', action="store_true", help="Skip the validation of submission")
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

        spinner = self.console.status("Loading submission !")
        spinner.start()

        sub_dir = Path(argv.submission_dir)
        if not sub_dir.is_dir():
            error_console.log(f"Submission directory given does not exist !!!")
            sys.exit(1)

        load_args = {}
        if 'all' not in argv.sets and len(argv.sets) > 0:
            load_args['sets'] = argv.sets

        if 'all' not in argv.tasks and len(argv.sets) > 0:
            load_args['tasks'] = argv.tasks

        load_args['score_dir'] = Path(argv.output)
        submission = bench.submission.load(path=sub_dir, **load_args)

        spinner.stop()
        self.console.print(":heavy_check_mark: Submission loaded successfully", style="bold green")

        if not argv.skip_validation:
            with self.console.status("Validating submission... ", spinner="aesthetic"):
                if not submission.valid:
                    error_console.print(f"Found Errors in submission: {submission.location}")
                    m_benchmark.show_errors(submission.validation_output)
                    sys.exit(1)

            self.console.print(":heavy_check_mark: Submission Valid", style="bold green")

        # load saved parameters
        self.console.print(f"Loaded parameters from :arrow_right: {submission.params_file}")
        submission.params_obj = submission.load_parameters()

        # update values from args
        submission.params.quiet = argv.quiet

        # Load & run benchmark
        benchmark = bench.benchmark(quiet=argv.quiet)
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
        (sub_dir / m_benchmark.BenchmarkParameters.file_stem).unlink(missing_ok=True)

        submission = bench.submission.load(path=sub_dir)
        self.console.log(f"Params file created/reset at @ {submission.params_file}")


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
        self.console.console.print(bench.benchmark.__doc__)
