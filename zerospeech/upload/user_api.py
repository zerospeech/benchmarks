import json
from datetime import datetime
from pathlib import Path
from typing import Union, Optional, Dict, Tuple, ClassVar, List

import requests
from pydantic import BaseModel, EmailStr, Field, AnyHttpUrl
from rich.console import Console
from zerospeech.settings import get_settings, Token

from .requests_w import get, post

_st = get_settings()
out = Console()


class APIHTTPException(Exception):
    def __init__(self, method: str, status_code: int, message: str):
        self.method = method
        self.status_code = status_code
        self.msg = message
        super().__init__(message)

    def __str__(self):
        """ String representation """
        return f"{self.method}: returned {self.status_code} => {self.msg}"


class NewModelInfo(BaseModel):
    """ Info required to create a new model id"""
    description: str
    gpu_budget: str
    train_set: str
    authors: str
    institution: str
    team: str
    paper_url: Optional[AnyHttpUrl]
    code_url: Optional[AnyHttpUrl]
    created_at: datetime = Field(default_factory=lambda: datetime.now())

    def clean_dict(self):
        return json.loads(self.json())


class SubmissionRequestFileIndexItem(BaseModel):
    filename: str
    filesize: int
    filehash: str = ""


class NewSubmissionInfo(BaseModel):
    """ Info required to create a new submission """
    model_id: str
    benchmark_id: str
    filename: str
    hash: str
    has_scores: bool
    multipart: bool
    index: Optional[List[SubmissionRequestFileIndexItem]]
    leaderboard: Optional[str]

    def clean_dict(self):
        return json.loads(self.json())


class _UserAPIMethods:
    """ Methods for communicating with the users-api on zerospeech.com """

    @staticmethod
    def login(credentials: Union[str, EmailStr], password) -> Optional[Token]:
        """ Request Session token from the API by providing valid credentials """
        route_url, _ = _st.api.request_params(route_name='user_login', token=None)

        response = post(
            route_url,
            data={
                "grant_type": "password",
                "username": credentials,
                "password": password,
                "scopes": [],
                "client_id": _st.api.client_id,
                "client_secret": _st.api.client_secret
            }
        )
        if response.status_code != 200:
            reason = response.json().get('detail', '')
            raise APIHTTPException(
                method="user_login", status_code=response.status_code, message=reason
            )
        return Token.parse_obj(response.json())

    @staticmethod
    def get_user_info(token: Token) -> Dict:
        route_url, headers = _st.api.request_params(route_name='user_info', token=token, username=token.username)

        response = get(
            route_url,
            headers=headers
        )
        if response.status_code != 200:
            reason = response.json().get('detail', '')
            raise APIHTTPException(
                method="user_info", status_code=response.status_code, message=reason
            )
        return response.json()

    @staticmethod
    def make_new_model(username: str, author_name: str, new_model_info: NewModelInfo, token: Token) -> str:
        route_url, headers = _st.api.request_params(
            route_name='new_model', token=token, username=username, author_name=author_name)

        response = post(
            route_url,
            json=new_model_info.clean_dict(),
            headers=headers
        )
        if response.status_code != 200:
            reason = response.json().get('detail', '')
            raise APIHTTPException(
                method="new_model", status_code=response.status_code, message=reason
            )
        return response.content.decode()

    @staticmethod
    def make_new_submission(username: str, new_sub_info: NewSubmissionInfo, token: Token) -> str:
        """ Create a new submission """
        route_url, headers = _st.api.request_params(
            route_name='new_submission', token=token, username=username)

        response = post(
            route_url,
            debug=True,
            json=new_sub_info.clean_dict(),
            headers=headers
        )
        if response.status_code != 200:
            reason = response.json().get('detail', '')
            raise APIHTTPException(
                method="new_submission", status_code=response.status_code, message=reason
            )
        return response.content.decode().replace('"', '').replace("'", "")


class CurrentUser(BaseModel):
    """ Dataclass Managing the current user session """
    username: str
    affiliation: str
    first_name: str
    last_name: str
    email: EmailStr
    token: Token
    session_file: ClassVar[Path] = _st.user_credentials

    @staticmethod
    def get_credentials_from_user():
        """ Prompt user for authentication credentials """
        out.print("Required credentials to perform authentication", style="yellow")
        username = out.input("username/email: ")
        password = out.input("password: ", password=True)
        return username, password

    def save(self):
        """ Save session to disk"""
        with self.session_file.open('w') as fp:
            fp.write(self.json(indent=4))

    @classmethod
    def clear(cls):
        """ Clear current user session """
        cls.session_file.unlink(missing_ok=True)

    @classmethod
    def login(cls, credentials: Optional[Tuple[str, str]] = None, auto_save: bool = True):
        """ Create a new user session

        Parameters:
            credentials: allows to specify login/password tuple, if its none the user is prompted.
            auto_save: specify whether to save session on disk (default: True)
        Returns:
            Current session
        """
        if credentials is None:
            credentials = cls.get_credentials_from_user()

        token = _UserAPIMethods.login(credentials[0], credentials[1])
        creds = cls(token=token, **_UserAPIMethods.get_user_info(token=token))
        if auto_save:
            creds.save()
        return creds

    @classmethod
    def load(cls) -> Optional["CurrentUser"]:
        """ Load existing session from disk """
        if not cls.session_file.is_file():
            return None

        with cls.session_file.open() as fp:
            return cls.parse_obj(json.load(fp))

    @classmethod
    def load_or_create(cls, credentials: Optional[Tuple[str, str]] = None):
        """ Load the existing session or create a new one if it is not present """
        if cls.session_file.is_file():
            return cls.load()
        return cls.login(credentials)

    def new_model_id(
            self, *, author_name: str, description: str, gpu_budget: str, train_set: str,
            authors: str, institution: str, team: str, paper_url: Optional[str], code_url: Optional[str]
    ) -> str:
        """ Create a new model id from the given information """
        model_dt = _UserAPIMethods.make_new_model(
            username=self.username,
            author_name=author_name,
            new_model_info=NewModelInfo.parse_obj(dict(
                description=description,
                gpu_budget=gpu_budget,
                train_set=train_set,
                authors=authors,
                institution=institution,
                team=team,
                paper_url=paper_url,
                code_url=code_url,
            )),
            token=self.token
        )
        return model_dt

    def make_new_submission(
            self, model_id: str, filename: str, filehash: str,
            has_scores: bool, leaderboard: str,
            index: Optional[List[SubmissionRequestFileIndexItem]] = None
    ):
        return _UserAPIMethods.make_new_submission(
            username=self.username,
            new_sub_info=NewSubmissionInfo(
                model_id=model_id,
                # todo setup way to fetch real id
                benchmark_id="test-challenge",
                filename=filename,
                hash=filehash,
                multipart=index is not None,
                has_scores=has_scores,
                leaderboard=leaderboard,
                index=index
            ),
            token=self.token
        )
