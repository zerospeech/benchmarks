import argparse
import sys
from pathlib import Path

from zerospeech.out import error_console, console as std_console
from zerospeech.settings import get_settings
from zerospeech.upload import SubmissionUploader, APIHTTPException, BenchmarkClosedError
from .cli_lib import CMD

st = get_settings()


class SubmitOnline(CMD):
    """ Submit your results to zerospeech.com """
    COMMAND = "submit"
    NAMESPACE = ""

    def init_parser(self, parser: argparse.ArgumentParser):
        parser.add_argument('-r', '--resume', action='store_true',
                            help='Try resuming submission from given directory')
        parser.add_argument('-q', '--quiet', action='store_true',
                            help="Do not print status information")
        parser.add_argument('-m', '--multipart', action='store_true',
                            help='Upload archive in multiple parts (better for large submissions)')
        parser.add_argument('submission_dir', type=Path,
                            help="The directory containing the submission")

    def run(self, argv: argparse.Namespace):
        std_console.print("Feature Not Yet Available !!!", style="red bold")

    def _run(self, argv: argparse.Namespace):
        try:
            if argv.resume:
                uploader = SubmissionUploader.resume(Path(argv.submission_dir), quiet=argv.quiet)
            else:
                uploader = SubmissionUploader.from_submission(
                    submission=Path(argv.submission_dir),
                    quiet=argv.quiet,
                    multipart=argv.multipart
                )

            if not uploader.ready:
                error_console.print("Oups :: Submission failed to prepare for upload, please try again !!!")
                sys.exit(1)

            # Upload
            uploader.upload()

            # clean-up
            uploader.clean()
        except APIHTTPException as e:
            error_console.print(e)
            sys.exit(1)
        except BenchmarkClosedError as e:
            error_console.print(e)
            sys.exit(1)
