import functools
import json
import shutil
from pathlib import Path
from typing import Tuple, Optional, Any, Union, Dict, TYPE_CHECKING

from pydantic import BaseModel
from rich.console import Console

from zerospeech.benchmarks import BenchmarkList
from zerospeech.data_loaders import zip_zippable
from zerospeech.out import void_console, console as std_console, error_console
from zerospeech.settings import get_settings
from zerospeech.httpw import post as http_post, get as http_get, APIHTTPException
from zerospeech.misc import ScoresNotFound, MetaYamlNotValid, InvalidSubmissionError
from zerospeech.submissions import show_errors
from .file_split import (
    FileUploadHandler, MultipartUploadHandler, SinglePartUpload, md5sum, UploadItem
)
from .user_api import CurrentUser, Token

if TYPE_CHECKING:
    from zerospeech.submissions import Submission

st = get_settings()


class BenchmarkClosedError(Exception):
    """ Benchmark not active or over deadline """
    pass


def get_first_author(authors: str) -> Tuple[str, str]:
    """ Returns a tuple containing first & last name of first author """
    try:
        raise NotImplementedError(f'Does not have an good author parser for {authors}')
    except (ValueError, NotImplementedError):
        # On failure fetch full name from user
        usr = CurrentUser.load()
        if usr:
            return usr.first_name, usr.last_name
        return "john", "doe"


def upload_submission(item: UploadItem, *, submission_id: str, token: Token):
    """ Function that performs upload of submission content to the api backend """

    route, headers = st.api.request_params(
        'submission_content_add', token=token, submission_id=submission_id, part_name=item.filepath.name
    )
    with item.filepath.open('rb') as file_data:
        files = dict(file=file_data)
        response = http_post(route, headers=headers, files=files, data={})

        if response.status_code != 200:
            raise APIHTTPException.from_request('submission_content_add', response)
        return response.json()


def get_submission_status(submission_id: str, token: Token) -> Dict[str, Any]:
    route, _ = st.api.request_params(
        "submission_status", token=token, submission_id=submission_id
    )

    response = http_get(route)

    if response.status_code != 200:
        raise APIHTTPException.from_request('submission_status', response)

    return response.json()


class UploadManifest(BaseModel):
    submission_location: Path
    multipart: bool
    benchmark_id: str
    tmp_dir: Optional[Path] = None
    archive_filename: Optional[str] = None
    submission_id: Optional[str] = None
    model_id: Optional[str] = None
    submission_validated: bool = False
    local_data_set: bool = False
    archive_created: bool = False
    quiet: bool = False
    is_test: bool = False

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

    @classmethod
    def resume(cls, tmp_dir: Path, quiet: bool = False) -> 'SubmissionUploader':
        """ Resume Uploader from a manifest file """
        man = UploadManifest.load(tmp_dir)
        if not quiet:
            std_console.print(f"Resuming upload from {tmp_dir}...")
        return cls(
            submission=man.submission_location,
            user_cred=None,
            quiet=quiet,
            **man.dict(exclude={'submission_location', 'user_logged_in', 'quiet'})
        )

    @classmethod
    def from_submission(
            cls, submission: Union[Path, "Submission"], usr: Optional[CurrentUser] = None,
            multipart: bool = True, quiet: bool = False
    ) -> 'SubmissionUploader':
        """ Create uploader from submission """
        return cls(
            submission=submission, user_cred=usr, multipart=multipart, quiet=quiet)

    def __init__(
            self, submission: Union[Path, "Submission"],
            user_cred: Union[CurrentUser, Tuple[str, str], None] = None,
            tmp_dir: Optional[Path] = None,
            archive_filename: Optional[str] = None,
            multipart: bool = True,
            quiet: bool = False,
            submission_validated: bool = False,
            local_data_set: bool = False,
            archive_created: bool = False,
            model_id: Optional[str] = None,
            submission_id: Optional[str] = None,
            is_test: bool = False,
            benchmark_id: str = ""
    ):
        self._quiet = quiet
        with self.console.status("building artifacts"):
            if isinstance(submission, Path):
                bench = BenchmarkList.from_submission(submission)

                # Check benchmark
                is_test = bench.is_test
                benchmark_id = bench.name
                if not bench.is_active():
                    raise BenchmarkClosedError(f"Benchmark {bench.name} does not accept submissions")

                submission = bench.submission.load(submission)

            self.submission = submission

            if user_cred is None:
                usr = CurrentUser.load()
                if usr is None:
                    creds = CurrentUser.get_credentials_from_user()
                    usr = CurrentUser.login(creds)
                self.user = usr
            elif isinstance(user_cred, CurrentUser):
                self.user = user_cred
            else:
                self.user = CurrentUser.login(user_cred)

            if tmp_dir is None:
                self.tmp_dir = st.mkdtemp(auto_clean=False)
            else:
                self.tmp_dir = tmp_dir

        self.console.print(f"UPLOAD DIR :::> {self.tmp_dir}")
        self.console.print("\tUse this directory to resume upload if it fails (--resume)", style="dark_orange3 italic")

        if archive_filename is None:
            self.archive_file = self.tmp_dir / f"{self.submission.location.name}.zip"
        else:
            self.archive_file = self.tmp_dir / archive_filename

        self.upload_handler: Optional[FileUploadHandler] = None

        self._manifest = UploadManifest(
            submission_location=self.submission.location,
            submission_validated=submission_validated,
            multipart=multipart,
            tmp_dir=self.tmp_dir,
            archive_filename=self.archive_file.name,
            submission_id=submission_id,
            model_id=model_id,
            local_data_set=local_data_set,
            archive_created=archive_created,
            is_test=is_test,
            benchmark_id=benchmark_id
        )
        self._manifest.save()

        # fetch system data & update submission
        with self.console.status("Building submission..."):
            if not self._manifest.local_data_set:
                self._fetch_local_data()

                # update manifest
                self._manifest.update('local_data_set', True)

        # check submission
        with self.console.status("Checking submission..."):
            if not self._manifest.submission_validated:
                self._check_submission()

                # update manifest
                self._manifest.update('submission_validated', True)

        with self.console.status("Checking model ID..."):
            if self._manifest.model_id is None:
                mdi = self._get_model_id()
                self.submission.meta.set_model_id(
                    submission_location=self.submission.location,
                    model_id=mdi
                )

                # update manifest
                self._manifest.update('model_id', mdi)

        # Making archive or load if existing
        self._make_archive(multipart)

        # update manifest
        self._manifest.update('archive_created', True)

        with self.console.status("Checking Submission ID"):
            if self._manifest.submission_id is None:
                self._register_submission()

        # make upload function
        self.upload_fn = functools.partial(
            upload_submission,
            submission_id=self.submission.meta.submission_id,
            token=self.user.token
        )
        self.console.print(":heavy_check_mark: Submission valid & ready for upload !!!", style="bold green")
        self.console.print(f"\t SUBMISSION_ID: {self._manifest.submission_id}", style="dark_orange3 italic")
        self.console.print(f"\t MODEL_ID: {self._manifest.model_id}", style="dark_orange3 italic")

    @property
    def console(self) -> Console:
        if self._quiet:
            return void_console
        return std_console

    @property
    def ready(self) -> bool:
        """Check if submission is ready for upload """
        if self._manifest.submission_id is None:
            error_console.print("No Submission ID")
            return False

        if self._manifest.model_id is None:
            error_console.print("No Model ID")
            return False

        if not self._manifest.submission_validated:
            error_console.print("Submission invalid")
            return False

        if not self._manifest.local_data_set:
            error_console.print("Failed to set all data (check user)")
            return False

        if not self._manifest.archive_created:
            error_console.print("No archive created")
            return False

        return True

    def _get_model_id(self) -> str:
        model_id = self.submission.meta.model_info.model_id
        authors = self.submission.meta.publication.authors
        if model_id is None:
            _, first_author_lname = get_first_author(authors)
            model_id = self.user.new_model_id(
                author_name=first_author_lname, description=self.submission.meta.model_info.system_description,
                gpu_budget=self.submission.meta.model_info.gpu_budget,
                train_set=self.submission.meta.model_info.train_set,
                authors=authors, author_label=f"{first_author_lname} et al.",
                institution=self.submission.meta.publication.institution,
                team=self.submission.meta.publication.team,
                paper_url=self.submission.meta.publication.paper_url,
                code_url=self.submission.meta.code_url
            )

        return model_id.replace('"', '').replace("'", "")

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
            raise MetaYamlNotValid('meta.yaml not valid', ctx=self.submission.meta.validation_context)

        # validate submission
        if not self.submission.valid:
            # todo convert submission validation to use context protocol
            show_errors(self.submission.validation_output)
            raise InvalidSubmissionError('submission not valid')

        # check scores (has_scores)
        if not self.submission.has_scores():
            raise ScoresNotFound('submission has no scores')

        # generate leaderboard
        scores = self.submission.get_scores()
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
        if self.submission.meta.submission_id is None:
            leaderboard_file = ""
            if self.submission.has_scores():
                leaderboard_file = str(self.submission.leaderboard_file.relative_to(self.submission.location))

            filehash = md5sum(self.archive_file)
            resp_obj = self.user.make_new_submission(
                model_id=self.submission.meta.model_info.model_id,
                filename=self.archive_file.name,
                filehash=filehash,
                benchmark_id=self._manifest.benchmark_id,
                has_scores=self.submission.has_scores(),
                leaderboard=leaderboard_file,
                index=self.upload_handler.api_index,
                author_label=self.submission.meta.publication.author_label,
                is_test=self._manifest.is_test
            )

            self.submission.meta.set_submission_id(
                submission_location=self.submission.location,
                submission_id=resp_obj
            )
        else:
            sub_status = get_submission_status(
                self.submission.meta.submission_id, self.user.token
            )
            status = sub_status.get("status", "")
            if status != "uploading":
                error_console.print(f"Submission {self.submission.meta.submission_id} has status '{status}' "
                                    f"and does not allow uploading")
                error_console.print("Remove the submission_id entry from the meta.yaml to upload to a different id")
                self.clean(True)
                raise ValueError('Cannot upload to current submission')

        # update manifest
        self._manifest.update('submission_id', self.submission.meta.submission_id)

    def clean(self, quiet: bool = False):
        """ Remove all temp files """
        if not quiet:
            with self.console.status("Cleaning up artifacts..."):
                shutil.rmtree(self.tmp_dir)
        else:
            shutil.rmtree(self.tmp_dir)

    def upload(self):
        """ Upload items to backend by iterating on upload handler"""
        with self.console.status("Uploading..."):
            for item in self.upload_handler:
                _ = self.upload_fn(item)
                self.upload_handler.mark_completed(item)
        self.console.print(":heavy_check_mark: upload successful !!", style="bold green")
