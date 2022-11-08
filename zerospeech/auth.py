import json
import sys
from pathlib import Path
from typing import Union, Optional, Dict, Tuple

from pydantic import BaseModel, EmailStr
from rich.console import Console
import requests

from .settings import get_settings

_st = get_settings()
out = Console()


class Token(BaseModel):
    __root__: bytes


class _UserAPI:
    """ Methods for communicating with the users-api on zerospeech.com """

    @staticmethod
    def login(credentials: Union[str, EmailStr], password) -> Optional[Token]:
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
        # todo check typing of response
        return Token.parse_obj(response.json().get("access_token"))

    @staticmethod
    def logout(token: Token):
        response = requests.delete(
            f"{_st.api_root}/auth/logout",
            headers=dict(Authorization=f"Bearer {token}")
        )
        # todo check way to propagate error code/message
        return response.status_code

    @staticmethod
    def get_user_info(token: Token) -> Dict:
        response = requests.get(
            f"{_st.api_root}/users/profile",
            headers=dict(Authorization=f"Bearer {token}")
        )
        if response.status_code != 200:
            # todo check way to propagate error code/message
            return {}
        return response.json()


class CurrentUser(BaseModel):
    username: str
    affiliation: str
    first_name: str
    last_name: str
    email: EmailStr
    token: Token

    @staticmethod
    def get_credentials_from_user():
        """ Request authentication credentials from user input"""
        out.print("Required credentials to perform authentication")
        username = out.input("username/email: ")
        password = out.input("password: ", password=True)
        return username, password

    def save(self, location: Path = _st.user_credentials):
        """ Save credentials to disk"""
        with location.open('w') as fp:
            fp.write(self.json(indent=4))

    def clear(self, location: Path = _st.user_credentials):
        """ Clear current user session """
        _UserAPI.logout(self.token)
        location.unlink()

    @classmethod
    def login(cls, credentials: Optional[Tuple[str, str]] = None):
        if credentials is None:
            credentials = cls.get_credentials_from_user()
        token = _UserAPI.login(credentials[0], credentials[1])
        # todo add failsafe ?
        creds = cls(token=..., **_UserAPI.get_user_info(token))
        creds.save()
        return creds

    @classmethod
    def load(cls, location: Path = _st.user_credentials):
        with location.open() as fp:
            data = json.load(fp)
        return cls(**data)

    @classmethod
    def load_or_create(cls, location: Path = _st.user_credentials, credentials: Optional[Tuple[str, str]] = None):
        """ Load the existing session or create a new one if it is not present """
        if location.is_file():
            return cls.load(location)
        return cls.login(credentials)


