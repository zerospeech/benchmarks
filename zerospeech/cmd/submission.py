import argparse

from .cli_lib import CMD


class Submission(CMD):
    """ Submission manager subcommand """
    COMMAND = "submission"
    NAMESPACE = ""

    def init_parser(self, parser: argparse.ArgumentParser):
        parser.print_help()

    def run(self, argv: argparse.Namespace):
        pass


class SubmissionInit(CMD):
    """ Initialise a directory for a specific benchmark """
    COMMAND = "init"
    NAMESPACE = "submission"

    def init_parser(self, parser: argparse.ArgumentParser):
        pass

    def run(self, argv: argparse.Namespace):
        pass


class SubmissionVerify(CMD):
    """ Verify the validity of a submission """
    COMMAND = "verify"
    NAMESPACE = "submission"

    def init_parser(self, parser: argparse.ArgumentParser):
        pass

    def run(self, argv: argparse.Namespace):
        pass


class SubmissionZip(CMD):
    """ Create a zip archive of a submission """
    COMMAND = "zip"
    NAMESPACE = "submission"

    def init_parser(self, parser: argparse.ArgumentParser):
        pass

    def run(self, argv: argparse.Namespace):
        pass


class SubmissionUpload(CMD):
    """ Upload a submission to zerospeech.com """
    COMMAND = "upload"
    NAMESPACE = "submission"

    def init_parser(self, parser: argparse.ArgumentParser):
        pass

    def run(self, argv: argparse.Namespace):
        pass
