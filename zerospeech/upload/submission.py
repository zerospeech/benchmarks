import functools
import json
import shutil
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
    FileUploadHandler, MultipartUploadHandler, SinglePartUpload, md5sum, UploadItem
)
from .user_api import CurrentUser, Token, APIHTTPException
from .requests_w import post

st = get_settings()


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
    # note: this is not needed (does 'requests' library auto-set content-type ????)
    # headers["Content-Type"] = f"multipart/form-data; boundary={item.filehash}"

    with item.filepath.open('rb') as fp:
        files = dict(
            file_data=fp.read()
        )

    resp = post(route, headers=headers, files=files, data={})

    if resp.status_code != 200:
        reason = resp.json().get('detail', '')
        raise APIHTTPException(
            method="upload_submission", status_code=resp.status_code, message=reason
        )

    return resp.json(), resp.status_code


class UploadManifest(BaseModel):
    submission_location: Path
    multipart: bool
    tmp_dir: Optional[Path] = None
    archive_filename: Optional[str] = None
    submission_id: Optional[str] = None
    model_id: Optional[str] = None
    submission_validated: bool = False
    local_data_set: bool = False
    archive_created: bool = False
    quiet: bool = False

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

        return cls(
            submission=man.submission_location,
            user_cred=None,
            quiet=quiet,
            **man.dict(exclude={'submission_location', 'user_logged_in', 'quiet'})
        )

    @classmethod
    def from_submission(
            cls, submission: Union[Path, m_benchmark.Submission], usr: Optional[CurrentUser] = None,
            multipart: bool = True, quiet: bool = False
    ) -> 'SubmissionUploader':
        """ Create uploader from submission """
        return cls(
            submission=submission, user_cred=usr, multipart=multipart, quiet=quiet)

    def __init__(
            self, submission: Union[Path, m_benchmark.Submission],
            user_cred: Union[CurrentUser, Tuple[str, str], None] = None,
            tmp_dir: Optional[Path] = None,
            archive_filename: Optional[str] = None,
            multipart: bool = True,
            quiet: bool = False,
            submission_validated: bool = False,
            local_data_set: bool = False,
            archive_created: bool = False,
            model_id: Optional[str] = None,
            submission_id: Optional[str] = None
    ):
        self._quiet = quiet
        if isinstance(submission, Path):
            bench = BenchmarkList.from_submission(submission)
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

        self.console.print(f"Upload dir:::> {self.tmp_dir}")

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
            archive_created=archive_created
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

    @property
    def console(self) -> Console:
        if self._quiet:
            return void_console
        return std_console

    @property
    def ready(self) -> bool:
        """Check if submission is ready for upload """
        if self._manifest.submission_id is None:
            print("No Submission ID")
            return False

        if self._manifest.model_id is None:
            print("No Model ID")
            return False

        if not self._manifest.submission_validated:
            print("Submission invalid")
            return False

        if not self._manifest.local_data_set:
            print("Failed to set all data (check user)")
            return False

        if not self._manifest.archive_created:
            print("No archive created")
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
                authors=authors,
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
                has_scores=self.submission.has_scores(),
                leaderboard=leaderboard_file,
                index=self.upload_handler.api_index()
            )

            self.submission.meta.set_submission_id(
                submission_location=self.submission.location,
                submission_id=resp_obj
            )

        # update manifest
        self._manifest.update('submission_id', self.submission.meta.submission_id)

    def clean(self):
        """ Remove all temp files """
        shutil.rmtree(self.tmp_dir)

    def upload(self):
        """ Upload items to backend by iterating on upload handler"""
        for item in self.upload_handler:
            msg, code = self.upload_fn(item)
            if code == 200:
                self.upload_handler.mark_completed(item)