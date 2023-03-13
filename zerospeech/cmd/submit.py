import argparse
import sys
from pathlib import Path

import requests
from pydantic import parse_obj_as, ValidationError

from zerospeech.upload import SubmissionUploader
from zerospeech.out import warning_console, console as std, error_console
from zerospeech.settings import get_settings
from .cli_lib import CMD

st = get_settings()

SUBMIT_AVAILABLE_MSG = """
[blink bold red uu on white]Submissions are now open[/blink bold red uu on white]
   
You need to update this module to be able to use the submit option.

You can run: 

    pip install -U "zerospeech-benchmarks\[all]"

Further instructions can be found @ [Toolbox documentation](https://version2.zerospeech.com/toolbox/#upload)
"""

SUBMIT_WIP_MESSAGE = """
[large][red]The submit functionality is a Work In Progress[/red][/large]

It will be available soon !!! 

An announcement will be made on our news section https://version2.zerospeech.com/news/

If you have any questions please contact us @ mailto:contact@zerospeech.com
"""


def is_submit_available():
    resp = requests.get(str(st.submit_available_url))
    if resp.status_code != 200:
        return False
    try:
        return parse_obj_as(bool, resp.content)
    except ValidationError:
        return False


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
