import argparse

from rich.table import Table

from .cli_lib import CMD
from ..datasets import DatasetsDir
from ..out import console


class DatasetCMD(CMD):
    """ Manipulate Datasets """
    COMMAND = "datasets"
    NAMESPACE = ""

    def init_parser(self, parser: argparse.ArgumentParser):
        parser.add_argument("--local", action="store_true", help="List local datasets only")

    def run(self, argv: argparse.Namespace):
        datasets_dir = DatasetsDir.load()

        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Name")
        table.add_column("Origin")
        table.add_column("Size")
        table.add_column("Installed")

        if argv.local:
            dt_list = datasets_dir.datasets
        else:
            dt_list = datasets_dir.available_datasets

        for d in dt_list:
            dts = datasets_dir.get(d)
            table.add_row(
                dts.name, dts.origin.origin_host, dts.origin.size_label, f"{dts.installed}"
            )

        console.print(table)


class PullDatasetCMD(CMD):
    """ Download a dataset """
    COMMAND = "pull"
    NAMESPACE = "datasets"

    def init_parser(self, parser: argparse.ArgumentParser):
        parser.add_argument('name')

    def run(self, argv: argparse.Namespace):
        datasets = DatasetsDir.load()
        dataset = datasets.get(argv.name)
        dataset.pull(show_progress=True)
