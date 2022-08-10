import argparse
import sys
import webbrowser
import platform
import urllib.parse

from .cli_lib import CMD
from ..settings import get_settings

st = get_settings()


class HelpCMD(CMD):
    """  """
    COMMAND = "support"
    NAMESPACE = ""

    def init_parser(self, parser: argparse.ArgumentParser):
        pass

    def run(self, argv: argparse.Namespace):
        pass


class AskHelpCMD(CMD):
    """ Send an email to ask for help """
    COMMAND = "email"
    NAMESPACE = "support"

    def init_parser(self, parser: argparse.ArgumentParser):
        pass

    def run(self, argv: argparse.Namespace):
        os_info = urllib.parse.quote(f"{platform.system()}-{platform.release()}-{platform.version()}")
        py_info = urllib.parse.quote(f"{sys.version}".replace('\n', ''))
        # todo add installed packages from pip / conda
        tech_info = f'%0D%0A%0D%0A%5BINFO%5D%3A%0D%0AOS%3A%20{os_info}%0D%0APYTHON%3A%20{py_info}'
        url = f'mailto:{st.admin_email}?subject=%5BZR-BENCHMARK%5D%5BSUPPORT%5D&body={tech_info}'
        webbrowser.open(url, new=1)


class DocumentationCMD(CMD):
    """ Opens our documentation """
    COMMAND = "docs"
    NAMESPACE = "support"

    def init_parser(self, parser: argparse.ArgumentParser):
        pass

    def run(self, argv: argparse.Namespace):
        webbrowser.open(f'https://zerospeech.com/', new=1)
