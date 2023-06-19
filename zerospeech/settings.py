import atexit
import functools
import os
import shutil
import tempfile
from datetime import datetime, timedelta
from functools import lru_cache
from pathlib import Path
from tempfile import gettempdir
from typing import Dict, Tuple, Any, Optional, Union, Callable

from pydantic import (
    BaseSettings,
    AnyHttpUrl,
    parse_obj_as,
    validator,
    DirectoryPath,
    Field,
    EmailStr, BaseModel,
)

StrOrCallable = Union[str, Callable[..., str]]

API_URL = os.environ.get('_DEV_API_URL', 'https://api.cognitive-ml.fr')


class Token(BaseModel):
    """ Dataclass defining a session token"""
    username: str
    access_token: str
    token_type: str
    expiry: datetime = Field(default_factory=lambda: datetime.now() + timedelta(days=5))

    def is_expired(self) -> bool:
        return datetime.now() > self.expiry


class ZerospeechAPI(BaseModel):
    client_id: str = "zrc-commandline-benchmark-tool"
    client_secret: str = "wIBhXvNDTZ2xtDh3k0MJGWx+dAFohlKkGfFwV101CWo="
    API_URL: AnyHttpUrl = parse_obj_as(AnyHttpUrl, API_URL)
    API_ROUTES = {
        "user_login": '/auth/login',
        "benchmark_info": functools.partial(
            lambda benchmark_id: f'/benchmarks/{benchmark_id}/info'
        ),
        "user_info": functools.partial(lambda username: f'/users/{username}/profile'),
        "new_model": functools.partial(
            lambda username, author_name: f'/users/{username}/models/create?author_name={author_name}'),
        "new_submission": functools.partial(lambda username: f'/users/{username}/submissions/create'),
        "submission_content_add": functools.partial(
            lambda submission_id, part_name: f'/submissions/{submission_id}/content/add?part_name={part_name}'),
        "submission_status": functools.partial(
            lambda submission_id: f"/submissions/{submission_id}/content/status"
        )
    }

    @staticmethod
    def build_api_headers(token: Optional[Token]):
        """ Build correct headers for connecting with the zerospeech API"""
        if token is None:
            return dict()

        if token.is_expired():
            raise ValueError('token is expired, please create a new session')
        headers = {}

        if token.token_type == 'bearer':
            headers['Authorization'] = f"Bearer {token.access_token}"

        return headers

    def request_params(self, route_name: str, token: Optional[Token] = None, **kwargs) -> Tuple[StrOrCallable, Dict[str, Any]]:
        """ Build params for sending request to api """
        sub_route = self.API_ROUTES.get(route_name, None)
        if sub_route is None:
            raise ValueError(f'route {route_name} does not exist')

        if callable(sub_route):
            sub_route = sub_route(**kwargs)

        route_url = f"{self.API_URL}{sub_route}"

        return route_url, self.build_api_headers(token)


class ZerospeechBenchmarkSettings(BaseSettings):
    APP_DIR: Path = Path.home() / "zr-data"
    TMP_DIR: DirectoryPath = Path(gettempdir())
    repo_origin: AnyHttpUrl = parse_obj_as(
        AnyHttpUrl, "https://download.zerospeech.com/repo.json"
    )
    admin_email: EmailStr = parse_obj_as(EmailStr, "nicolas.hamilakis@ens.psl.eu")
    api: ZerospeechAPI = ZerospeechAPI()

    @validator("repo_origin", pre=True)
    def cast_url(cls, v):
        """ Cast strings to AnyHttpUrl """
        if isinstance(v, str):
            return parse_obj_as(AnyHttpUrl, v)
        return v

    @property
    def dataset_path(self) -> Path:
        """ Path to dataset storage folder """
        return self.APP_DIR / "datasets"

    @property
    def samples_path(self) -> Path:
        """ Path to samples storage folder """
        return self.APP_DIR / "samples"

    @property
    def checkpoint_path(self) -> Path:
        """ Path to checkpoint folder """
        return self.APP_DIR / "checkpoints"

    @property
    def repository_index(self) -> Path:
        """ Path to local repository index """
        return self.APP_DIR / "repo.json"

    @property
    def user_credentials(self):
        return self.APP_DIR / "creds.json"

    @property
    def submit_available_url(self) -> AnyHttpUrl:
        """ URL to check if submit is available """
        return parse_obj_as(
            AnyHttpUrl, f"{str(self.api.API_URL)}/_private/submit-available"
        )

    def mkdtemp(self, auto_clean: bool = True) -> Path:
        tmp_loc = Path(tempfile.mkdtemp(prefix="zeroC", dir=self.TMP_DIR))

        def clean_tmp(d):
            shutil.rmtree(d)

        if auto_clean:
            # create an auto-clean action
            atexit.register(clean_tmp, d=tmp_loc)

        return tmp_loc


@lru_cache()
def get_settings() -> ZerospeechBenchmarkSettings:
    """ Build & return global settings """
    env_file = os.environ.get("ZR_ENV", None)

    if env_file:
        return ZerospeechBenchmarkSettings(
            _env_file=env_file, _env_file_encoding="utf-8"
        )
    return ZerospeechBenchmarkSettings()
