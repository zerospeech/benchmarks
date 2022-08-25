import argparse

from .cli_lib import CMD


class User(CMD):
    """ User management command """
    COMMAND = "user"
    NAMESPACE = ""

    def init_parser(self, parser: argparse.ArgumentParser):
        parser.print_help()

    def run(self, argv: argparse.Namespace):
        pass


class UserLogin(CMD):
    """ User loging to the zerospeech.com platform """
    COMMAND = "login"
    NAMESPACE = "user"

    def init_parser(self, parser: argparse.ArgumentParser):
        pass

    def run(self, argv: argparse.Namespace):
        pass


class UserClear(CMD):
    """ Clear the saved login """
    COMMAND = "login"
    NAMESPACE = "user"

    def init_parser(self, parser: argparse.ArgumentParser):
        pass

    def run(self, argv: argparse.Namespace):
        pass
