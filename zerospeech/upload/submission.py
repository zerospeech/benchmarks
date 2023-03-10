import json
from pathlib import Path
from typing import Tuple, Optional, Any, Union

from pydantic import BaseModel
from rich.console import Console

from zerospeech.benchmarks import BenchmarkList
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


class UploadManifest(BaseModel):
    submission_location: Path
    submission_validated: bool
    multipart: bool
    user_logged_in: bool
    tmp_dir: Path
    archive_filename: str
    submission_id: str
    model_id: str

    @staticmethod
    def index_stem() -> str:
        return ".manifest"

    @classmethod
    def load(cls, location: Path):
        """ Load Manifest from location """
        if not (location / cls.index_stem()).is_file():
            raise FileNotFoundError("No Index file")

        with (location / cls.index_stem()).open() as fp:
            return cls.parse_obj(json.load(fp))

    def save(self):
        """ Save to disk """
        with (self.tmp_dir / self.index_stem()).open('w') as fp:
            fp.write(self.json(indent=4))

    def update(self, field: str, value: Any):
        """ Update a field """
        setattr(self, field, value)
        self.save()


class SubmissionUploader:

    def __init__(
            self, submission: Union[Path, m_benchmark.Submission] , credentials: Tuple[str, str],
            multipart: bool = True, quiet: bool = False
    ):
        if isinstance(submission, Path):
            bench = BenchmarkList.from_submission(submission)
            submission = bench.submission.load(submission)


        # todo: add check for if resume exists
        # todo generic submission loader in misc of benchmark (??)
        self.upload_handler: Optional[FileUploadHandler] = None
        self.submission = submission
        self.tmp_dir = st.mkdtemp(auto_clean=False)
        self.archive_file = self.tmp_dir / f"{submission.location.name}.zip"
        self._quiet = quiet
        # load or create user
        self.user = CurrentUser.login(credentials)

        self._manifest = UploadManifest(
            submission_location=submission.location,
            submission_validated=False,
            multipart=multipart,
            user_logged_in=self.user is not None,
            tmp_dir=self.tmp_dir,
            archive_filename=self.archive_file.name,
            submission_id="",
            model_id=""
        )
        self._manifest.save()

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

        if not self.submission.meta.is_valid():
            raise m_benchmark.MetaYamlNotValid('meta.yaml not valid', ctx=self.submission.meta.validation_context)

        # validate submission
        if not self.submission.valid:
            # todo convert submission validation to use context protocol
            m_benchmark.show_errors(self.submission.validation_output)
            raise m_benchmark.InvalidSubmissionError('submission not valid')

        # check scores (has_scores)
        if not self.submission.has_scores():
            raise m_benchmark.ScoresNotFound('submission has no scores')

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
