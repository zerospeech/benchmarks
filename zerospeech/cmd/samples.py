
import argparse

from rich.padding import Padding
from rich.table import Table

from .cli_lib import CMD
from ..model import samples
from ..networkio import check_update_repo_index, update_repo_index
from ..out import console, error_console
from ..settings import get_settings

st = get_settings()


class SamplesCMD(CMD):
    """ Manipulate Samples """
    COMMAND = "samples"
    NAMESPACE = ""

    def init_parser(self, parser: argparse.ArgumentParser):
        parser.add_argument("--local", action="store_true", help="List local checkpoint only")

    def run(self, argv: argparse.Namespace):
        samples_dir = samples.SamplesDir.load()

        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Name")
        table.add_column("Origin")
        table.add_column("Size")
        table.add_column("Installed")

        if argv.local:
            dt_list = samples_dir.items
        else:
            dt_list = samples_dir.available_items

        for d in dt_list:
            dts = samples_dir.get(d)
            if dts.origin.type == 'internal':
                host = st.repo_origin.host
            else:
                host = "external"

            table.add_row(
                dts.name, host, dts.origin.size_label, f"{dts.installed}"
            )

        console.print(Padding(f"==> RootDir: {samples_dir.root_dir}", (1, 0, 1, 0), style="bold grey70", expand=False))
        console.print(table)


class PullSampleCMD(CMD):
    """ Download a sample """
    COMMAND = "pull"
    NAMESPACE = "samples"

    def init_parser(self, parser: argparse.ArgumentParser):
        parser.add_argument('name')
        parser.add_argument('-u', '--skip-verification', action='store_true', help="Skip archive verification")
        parser.add_argument('-q', '--quiet', action='store_true', help='Suppress download info output')

    def run(self, argv: argparse.Namespace):
        # update repo index if necessary
        if check_update_repo_index():
            update_repo_index()

        sample_dir = samples.SamplesDir.load()
        sample_itm = sample_dir.get(argv.name, cls=samples.SampleItem)
        sample_itm.pull(quiet=argv.quiet, show_progress=True, verify=not argv.skip_verification)


class RemoveSampleCMD(CMD):
    """ Remove a sample item """
    COMMAND = "rm"
    NAMESPACE = "samples"

    def init_parser(self, parser: argparse.ArgumentParser):
        parser.add_argument('name')

    def run(self, argv: argparse.Namespace):
        sample_dir = samples.SamplesDir.load()
        smp = sample_dir.get(argv.name)
        if smp:
            smp.uninstall()
            console.log("[green] Dataset uninstalled successfully !")
        else:
            error_console.log(f"Failed to find dataset named :{argv.name}")
