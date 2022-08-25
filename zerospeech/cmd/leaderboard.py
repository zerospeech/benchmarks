import argparse

from .cli_lib import CMD


class Leaderboard(CMD):
    """ Leaderboard manager subcommand """
    COMMAND = "leaderboard"
    NAMESPACE = ""

    def init_parser(self, parser: argparse.ArgumentParser):
        parser.print_help()

    def run(self, argv: argparse.Namespace):
        pass


class LeaderboardGenerate(CMD):
    """ Generate a leaderboard entry """
    COMMAND = "generate"
    NAMESPACE = "leaderboard"

    def init_parser(self, parser: argparse.ArgumentParser):
        pass

    def run(self, argv: argparse.Namespace):
        pass


class LeaderboardUpload(CMD):
    """ Upload a leaderboard entry to zerospeech.com """
    COMMAND = "upload"
    NAMESPACE = "leaderboard"

    def init_parser(self, parser: argparse.ArgumentParser):
        pass

    def run(self, argv: argparse.Namespace):
        pass
