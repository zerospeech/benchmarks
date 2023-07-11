import argparse
import sys
from pathlib import Path

from zerospeech.benchmarks import BenchmarkList
from zerospeech.out import error_console, warning_console, console as std_console
from zerospeech.submissions import MetaFile, show_errors
from zerospeech.tasks import BenchmarkParameters
from .cli_lib import CMD


class Submission(CMD):
    """ Submission manager subcommand """
    COMMAND = "submission"
    NAMESPACE = ""

    def init_parser(self, parser: argparse.ArgumentParser):
        parser.print_help()

    def run(self, argv: argparse.Namespace):
        """ """
        pass


class SubmissionInit(CMD):
    """ Initialise a directory for a specific benchmark """
    COMMAND = "init"
    NAMESPACE = "submission"

    def init_parser(self, parser: argparse.ArgumentParser):
        parser.add_argument("name")
        parser.add_argument("location")

    def run(self, argv: argparse.Namespace):
        try:
            benchmark_type = BenchmarkList(argv.name)
        except ValueError:
            error_console.log(f"Specified benchmark ({argv.name}) does not exist !!!!")
            warning_console.log(f"Use one of the following : {','.join(b for b in BenchmarkList)}")
            sys.exit(1)

        # Load benchmark
        benchmark = benchmark_type.benchmark(quiet=argv.quiet)

        location = Path(argv.location)
        if location.is_dir():
            error_console.log("Location specified already exists !!!")
            sys.exit(2)

        with std_console.status("Initialising submission dir"):
            benchmark.init_submission_dir(location)

        std_console.print(f"Submission directory created @ {location}", style="green bold")


class BenchmarkParamsCMD(CMD):
    """ Create template params.yaml """
    COMMAND = "params"
    NAMESPACE = "submission"

    def init_parser(self, parser: argparse.ArgumentParser):
        parser.add_argument("submission_dir")
        parser.add_argument('-r', '--reset', action="store_true", help="Reset params.yaml to default values")

    def run(self, argv: argparse.Namespace):
        location = Path(argv.submission_dir)
        if not location.is_dir():
            error_console("Location specified does not exist !!!")
            sys.exit(2)

        benchmark_name = None
        try:
            benchmark_name = MetaFile.benchmark_from_submission(location)
            if benchmark_name is None:
                raise TypeError("benchmark not found")

            benchmark_type = BenchmarkList(benchmark_name)
        except TypeError:
            error_console.log(f"Specified submission does not have a valid {MetaFile.file_stem}"
                              f"\nCannot find benchmark type")
            sys.exit(1)
        except ValueError:
            error_console.log(f"Specified benchmark ({benchmark_name}) does not exist !!!!")
            warning_console.log(f"Use one of the following : {','.join(b for b in BenchmarkList)}")
            sys.exit(1)

        # Load benchmark
        benchmark = benchmark_type.benchmark(quiet=argv.quiet)

        if argv.reset:
            # remove old params file if exists
            (location / BenchmarkParameters.file_stem).unlink(missing_ok=True)

        submission = benchmark.load_submission(location)
        if argv.reset:
            self.console.log(f"Params file created/reset at @ {submission.params_file}")

        self.console.print(submission.params)


class SubmissionVerify(CMD):
    """ Verify the validity of a submission """
    COMMAND = "verify"
    NAMESPACE = "submission"

    def init_parser(self, parser: argparse.ArgumentParser):
        parser.add_argument("location")

    def run(self, argv: argparse.Namespace):
        location = Path(argv.location)
        if not location.is_dir():
            error_console("Location specified does not exist !!!")
            sys.exit(2)

        benchmark_name = None
        try:
            benchmark_name = MetaFile.benchmark_from_submission(location)
            if benchmark_name is None:
                raise TypeError("benchmark not found")

            benchmark_type = BenchmarkList(benchmark_name)
        except TypeError:
            error_console.log(f"Specified submission does not have a valid {MetaFile.file_stem}"
                              f"\nCannot find benchmark type")
            sys.exit(1)
        except ValueError:
            error_console.log(f"Specified benchmark ({benchmark_name}) does not exist !!!!")
            warning_console.log(f"Use one of the following : {','.join(b for b in BenchmarkList)}")
            sys.exit(1)

        # Load benchmark
        benchmark = benchmark_type.benchmark(quiet=argv.quiet)
        submission = benchmark.load_submission(location)
        with std_console.status(f"Validating submission @ {location}"):
            _ = submission.valid

        if submission.valid:
            std_console.print(f"Submission @ {location} is a valid submission for {bench} :heavy_check_mark:",
                              style='bold green')
        else:
            show_errors(submission.validation_output)
