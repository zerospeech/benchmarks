import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Union, Optional, Dict, Tuple, ClassVar

import requests
from pydantic import BaseModel, EmailStr, Field
from rich.console import Console

from .settings import get_settings

_st = get_settings()
out = Console()


class _Token(BaseModel):
    """ Dataclass defining a session token"""
    access_token: str
    token_type: str
    expiry: datetime = Field(default_factory=lambda: datetime.now() + timedelta(days=5))

    def is_expired(self) -> bool:
        return datetime.now() > self.expiry


def build_api_headers(token: _Token):
    """ Build correct headers for connecting with the zerospeech API"""
    if token.is_expired():
        raise ValueError('token is expired, please create a new session')
    headers = {}

    if token.token_type == 'bearer':
        headers['Authorization'] = f"Bearer {token.access_token}"

    return headers


class _UserAPI:
    """ Methods for communicating with the users-api on zerospeech.com """

    @staticmethod
    def login(credentials: Union[str, EmailStr], password) -> Optional[_Token]:
        """ Request Session token from the API by providing valid credentials """
        response = requests.post(
            f'{_st.api_root}/auth/login',
            data={
                "grant_type": "password",
                "username": credentials,
                "password": password,
                "scopes": [],
                "client_id": _st.client_id,
                "client_secret": _st.client_secret
            }
        )
        if response.status_code != 200:
            # todo check way to propagate error code/message
            return None
        return _Token.parse_obj(response.json())

    @staticmethod
    def get_user_info(token: _Token) -> Dict:
        response = requests.get(
            f"{_st.api_root}/users/profile",
            headers=build_api_headers(token)
        )
        if response.status_code != 200:
            # todo check way to propagate error code/message
            return {}
        return response.json()


class CurrentUser(BaseModel):
    """ Dataclass Managing the current user session """
    username: str
    affiliation: str
    first_name: str
    last_name: str
    email: EmailStr
    token: _Token
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

        token = _UserAPI.login(credentials[0], credentials[1])
        if token is None:
            raise ValueError('Authentication failed')
        creds = cls(token=token, **_UserAPI.get_user_info(token))
        if auto_save:
            creds.save()
        return creds

    @classmethod
    def load(cls) -> Optional["CurrentUser"]:
        """ Load existing session from disk """
        if not cls.session_file.is_file():
            return None

        with cls.session_file.open() as fp:
            data = json.load(fp)
        return cls(**data)

    @classmethod
    def load_or_create(cls, credentials: Optional[Tuple[str, str]] = None):
        """ Load the existing session or create a new one if it is not present """
        if cls.session_file.is_file():
            return cls.load()
        return cls.login(credentials)
