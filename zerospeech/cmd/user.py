import argparse
import sys

from rich.prompt import Confirm
from rich.table import Table

from .cli_lib import CMD
from ..out import console as std_console, error_console, warning_console
from ..auth import CurrentUser


class User(CMD):
    """ User management command """
    COMMAND = "user"
    NAMESPACE = ""

    def init_parser(self, parser: argparse.ArgumentParser):
        pass

    def run(self, argv: argparse.Namespace):
        current = CurrentUser.load()
        if current is None:
            error_console.print("No current user session, please use login to create a session !")
            sys.exit(1)

        table = Table(show_header=False)
        table.add_column("****")
        table.add_column("****")

        table.add_row("Username", current.username)
        table.add_row("Email", current.email)
        table.add_row("Affiliation", current.affiliation)
        table.add_row("Session Expiry", current.token.expiry.strftime("%m/%d/%Y, %H:%M:%S"))

        std_console.print(table)


class UserLogin(CMD):
    """ User loging to the zerospeech.com platform """
    COMMAND = "login"
    NAMESPACE = "user"

    def init_parser(self, parser: argparse.ArgumentParser):
        pass

    def run(self, argv: argparse.Namespace):
        if CurrentUser.session_file.is_file():
            CurrentUser.clear()
        try:
            usr = CurrentUser.login()
            std_console.print(f"User {usr.username} was logged in successfully !", style="bold green")
        except ValueError:
            error_console.print("User authentication failed, bad credentials")


class UserClear(CMD):
    """ Clear the saved login """
    COMMAND = "clear"
    NAMESPACE = "user"

    def init_parser(self, parser: argparse.ArgumentParser):
        pass

    def run(self, argv: argparse.Namespace):
        if Confirm("Are you sure you want to clear the current session ?", console=warning_console):
            CurrentUser.clear()

