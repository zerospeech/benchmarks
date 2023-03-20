import argparse
import sys
from pathlib import Path

from zerospeech.out import console as std, error_console
from zerospeech.settings import get_settings
from zerospeech.upload import SubmissionUploader, APIHTTPException
from .cli_lib import CMD

st = get_settings()


class SubmitOnline(CMD):
    """ Submit your results to zerospeech.com """
    COMMAND = "submit"
    NAMESPACE = ""

    def init_parser(self, parser: argparse.ArgumentParser):
        parser.add_argument('-r', '--resume-dir', action='store_true',
                            help='Try resuming submission from given directory')
        parser.add_argument('-q', '--quiet', action='store_true',
                            help="Do not print status information")
        parser.add_argument('-m', '--multipart', action='store_true',
                            help='Upload archive in multiple parts (better for large submissions)')
        parser.add_argument('submission_dir', type=Path,
                            help="The directory containing the submission")

    def run(self, argv: argparse.Namespace):
        try:
            if argv.resume_dir:
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
            std.print(":heavy_check_mark: Submission Uploaded Successfully !!!", style="bold green")

            # clean-up
            uploader.clean()
        except APIHTTPException as e:
            error_console.print(e)
            error_console.print(' '.join(eval(e.trace)))
            sys.exit(1)
