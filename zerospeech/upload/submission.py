from typing import Tuple, Optional

from rich.console import Console

from zerospeech.data_loaders import zip_zippable
from zerospeech.model import m_benchmark
from zerospeech.out import void_console, console as std_console
from zerospeech.settings import get_settings
from .file_split import (
    FileUploadHandler, MultipartUploadHandler, SinglePartUpload
)
from .user_api import CurrentUser

st = get_settings()


def get_first_author(authors: str) -> Tuple[str, str]:
    """ Returns a tuple containing first & last name of first author """
    try:
        # todo parse authors from meta & return fist author (fname, lname)
        raise ValueError('bad author names')
    except ValueError:
        usr = CurrentUser.load()
        if usr:
            return usr.first_name, usr.last_name
        return "john", "doe"


class SubmissionUploader:

    def __init__(
            self, submission: m_benchmark.Submission, credentials: Tuple[str, str],
            multipart: bool = True, quiet: bool = False
    ):
        self.upload_handler: Optional[FileUploadHandler] = None
        self.submission = submission
        self.tmp_dir = st.mkdtemp(auto_clean=False)
        self.archive_file = self.tmp_dir / f"{submission.location.name}.zip"
        self._quiet = quiet
        # load or create user
        self.user = CurrentUser.login(credentials)

        # fetch system data & update submission
        with self.console.status("Building submission..."):
            self._fetch_local_data()
        # check submission
        with self.console.status("Checking submission..."):
            self._check_submission()

        with self.console.status("Checking model ID..."):
            self.submission.meta.set_model_id(
                submission_location=self.submission.location,
                model_id=self._get_model_id()
            )

        # Making archive
        self._make_archive(multipart)

        with self.console.status("Checking Submission ID"):
            self._register_submission()

        self.console.print(":heavy_check_mark: Submission valid & ready for upload !!!", style="bold green")

    @property
    def console(self) -> Console:
        if self._quiet:
            return void_console
        return std_console

    def _get_model_id(self) -> str:
        model_id = self.submission.meta.model_info.model_id
        authors = self.submission.meta.publication.authors
        if model_id is None:
            _, first_author_lname = get_first_author(authors)
            model_id = self.user.new_model_id(
                author_name=first_author_lname, description=self.submission.meta.model_info.system_description,
                gpu_budget=self.submission.meta.model_info.gpu_budget,
                train_set=self.submission.meta.model_info.train_set,
                authors=authors,
                institution=self.submission.meta.publication.institution,
                team=self.submission.meta.publication.team,
                paper_url=self.submission.meta.publication.paper_url,
                code_url=self.submission.meta.code_url
            )

        return model_id

    def _fetch_local_data(self):
        """ Fetch all system data & update meta.yaml """
        author_label = self.submission.meta.publication.author_label
        if "et al." not in author_label:
            first_author_fname, first_author_lname = get_first_author(
                self.submission.meta.publication.authors
            )
            author_label = f"{first_author_lname.title()}, {first_author_fname[0].upper()}. et al."

        self.submission.meta.set_system_values(
            submission_location=self.submission.location,
            username=self.user.username,
            author_label=author_label
        )

    def _check_submission(self):
        """ Performs all checks on submission before upload to API """
        # todo: submission checks
        # [ ] check meta.yaml (ask for more info hard-written rules)
        # validate submission
        if not self.submission.valid:
            m_benchmark.show_errors(self.submission.validation_output)
            raise ValueError('submission not valid')

        # check scores (has_scores)
        if not self.submission.has_scores():
            raise ValueError('submission has no scores')
        # generate leaderboard
        scores = self.submission.get_scores
        ld_data = scores.build_leaderboard()
        with (scores.location / scores.leaderboard_file_name).open("w") as fp:
            fp.write(ld_data.json(indent=4))
        # check model_id

    def _make_archive(self, multipart: bool = True):
        if not self.archive_file.is_file():
            with self.console.status("Creating Archive..."):
                zip_zippable(self.submission, self.archive_file)

        with self.console.status("Building manifest..."):
            if multipart:
                self.upload_handler = MultipartUploadHandler.create_or_load(
                    self.archive_file
                )
            else:
                self.upload_handler = SinglePartUpload.create_or_load(
                    self.archive_file
                )
        self.console.print(":heavy_check_mark: archive created !!", style="bold green")

    def _register_submission(self):
        if self.submission.meta.submission_id is not None:
            # todo make new submission
            resp_obj = self.user.make_new_submission(
                ...,
                token=self.user.token
            )
            # set in submission
            self.submission.meta.set_submission_id(
                submission_location=self.submission.location,
                submission_id=resp_obj
            )

    def upload(self):
        # todo: make uploader by iterating on upload_handler
        pass
