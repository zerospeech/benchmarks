
import argparse

from rich.table import Table

from .cli_lib import CMD
from ..model import samples
from ..out import console, error_console


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
            table.add_row(
                dts.name, dts.origin.origin_host, dts.origin.size_label, f"{dts.installed}"
            )

        console.print(table)


class PullSampleCMD(CMD):
    """ Download a sample """
    COMMAND = "pull"
    NAMESPACE = "samples"

    def init_parser(self, parser: argparse.ArgumentParser):
        parser.add_argument('name')
        parser.add_argument('-q', '--quiet', action='store_true', help='Suppress download info output')

    def run(self, argv: argparse.Namespace):
        sample_dir = samples.SamplesDir.load()
        dataset = sample_dir.get(argv.name, cls=samples.SampleItem)
        dataset.pull(quiet=argv.quiet, show_progress=True)


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
