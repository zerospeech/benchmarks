import argparse
import json
import sys
from pathlib import Path

import requests
from pydantic import parse_obj_as, ValidationError

from .cli_lib import CMD
from ..auth import CurrentUser
from ..benchmarks import BenchmarkList
from ..data_loaders import zip_zippable
from ..model import m_meta_file
from ..out import error_console, warning_console, console as std_console
from ..settings import get_settings

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
        parser.add_argument('submission_dir', type=Path, help="The directory containing the submission")

    @staticmethod
    def generate_leaderboard(submission, bench):
        """ Generate the leaderboard from the scores """
        params = submission.params
        meta_file = submission.meta
        scores = bench.score_dir(  # noqa: bad typing
            location=Path("abxLS-scores"),
            meta_file=meta_file,
            params=params
        )
        leaderboard = scores.build_leaderboard()
        as_json = leaderboard.json(indent=4)
        with submission.leaderboard_file.open('w') as fp:
            json.dump(as_json, fp, indent=4)
        std_console.print("==> Generated leaderboard")

    @staticmethod
    def load_submission(submission_dir: Path):
        if not submission_dir.is_dir():
            error_console(f"Location specified does not exist !!!")
            sys.exit(2)

        benchmark_name = None
        try:
            benchmark_name = m_meta_file.MetaFile.benchmark_from_submission(submission_dir)
            if benchmark_name is None:
                raise TypeError("benchmark not found")

            bench = BenchmarkList(benchmark_name)
        except TypeError:
            error_console.log(f"Specified submission does not have a valid {m_meta_file.MetaFile.file_stem}"
                              f"\nCannot find benchmark type")
            sys.exit(1)
        except ValueError:
            error_console.log(f"Specified benchmark ({benchmark_name}) does not exist !!!!")
            warning_console.log(f"Use one of the following : {','.join(b for b in BenchmarkList)}")
            sys.exit(1)

        submission = bench.submission.load(submission_dir)
        return submission, bench

    @staticmethod
    def check_submission(submission):
        """ Check if submission is valid """
        # a) source files
        # b) score files
        if not submission.score_dir.is_dir():
            error_console.log(f'Given directory {submission.score_dir} does not exist !')
            sys.exit(1)
        std_console.print("=> Loading scores...", style="chartreuse3")
        # c) meta.yaml (with required entries)
        # d) params.yaml
        pass

    @staticmethod
    def build_archive(submission):
        """ Create archive submission """
        archive_file = st.TMP_DIR / f"{submission.name}.upload.zip"
        with std_console.status("Compressing files..."):
            zip_zippable(submission, archive_file)

        std_console.print(f":pencil: Successfully written submission to archive {archive_file.name}")
        return archive_file

    @staticmethod
    def upload_submission(submission_archive, user):
        """ Upload archive to zerospeech.com """
        pass

    @staticmethod
    def check_user():
        """ Check current session or create if not present. """
        current = CurrentUser.load()
        if current is None:
            std_console.print('No user session found !!')
            std_console.print('Please use your credentials to login, or create an account on https://zerospeech.com')
            current = CurrentUser.login()
        return current

    def run(self, argv: argparse.Namespace):
        # 0) if current user is not logged in prompt for login
        # current_user = self.check_user()
        # 1) load submission
        # submission, bench = self.load_submission(argv.submission_dir)
        # 2) verify all components are valid
        # self.check_submission(submission)
        # 3) generate leaderboard.json
        # self.generate_leaderboard(submission, bench)
        # 4) create/verify model_id
        # todo: connect model_id with zerospeech.com
        # 5) zip all files
        # submission_archive = self.build_archive(submission)
        # 6) upload
        # self.upload_submission(submission_archive, current_user)

        if is_submit_available():
            warning_console.print(SUBMIT_AVAILABLE_MSG)
        else:
            warning_console.print(SUBMIT_WIP_MESSAGE)

