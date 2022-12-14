import argparse
import platform
import sys
import urllib.parse
import webbrowser
from importlib.metadata import version, PackageNotFoundError
from typing import Optional

from rich.table import Table

from .cli_lib import CMD
from ..settings import get_settings
from ..out import error_console, console as std_console

st = get_settings()


class Version(CMD):
    """ Print the current version used """
    COMMAND = "version"
    NAMESPACE = ""

    def init_parser(self, parser: argparse.ArgumentParser):
        pass

    @staticmethod
    def get_package_version(pkg_name: str) -> Optional[str]:
        try:
            return version(pkg_name)
        except PackageNotFoundError:
            # package is not installed
            return None

    def run(self, argv: argparse.Namespace):
        zr_bench = self.get_package_version("zerospeech-benchmarks")
        # benchmark versions
        abx = self.get_package_version("zerospeech-libriabx")
        abx2 = self.get_package_version("zerospeech-libriabx2")
        tde = self.get_package_version("zerospeech-tde")
        torch = version('torch')
        numpy = version('numpy')
        torchaudio = version('torchaudio')

        table = Table(show_header=False, header_style="bold magenta")
        table.add_column("Package")
        table.add_column("Version")

        if zr_bench is None:
            error_console.print("ERROR: module zerospeech-benchmark not installed locally")
            sys.exit(1)

        table.add_row("zerospeech-benchmarks", zr_bench, end_section=True)
        if abx:
            table.add_row("zerospeech-libriabx", abx)
        if abx2:
            table.add_row("zerospeech-libriabx2", abx2)
        if tde:
            table.add_row("zerospeech-tde", tde)
        if numpy:
            table.add_row("numpy", numpy)
        if torch:
            table.add_row("torch", torch)
        if torchaudio:
            table.add_row("torchaudio", torchaudio)
        table.add_row(end_section=True)

        table.add_row("python", sys.version, end_section=True)
        table.add_row("Operating System", platform.platform(aliased=True))

        std_console.print(table)


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
