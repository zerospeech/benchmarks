import argparse
import sys
from pathlib import Path

from rich.padding import Padding
from rich.table import Table

from zerospeech.datasets import DatasetsDir, Dataset
from zerospeech.misc import md5sum, extract
from zerospeech.networkio import check_update_repo_index, update_repo_index
from zerospeech.out import console, error_console, warning_console, void_console
from zerospeech.settings import get_settings
from .cli_lib import CMD

st = get_settings()


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
            dt_list = datasets_dir.items
        else:
            dt_list = datasets_dir.available_items

        for d in dt_list:
            dts = datasets_dir.get(d)
            if dts.origin.type == 'internal':
                host = st.repo_origin.host
            else:
                host = "external"

            table.add_row(
                dts.origin.name, host, dts.origin.size_label, f"{dts.installed}"
            )

        console.print(Padding(f"==> RootDir: {datasets_dir.root_dir}", (1, 0, 1, 0), style="bold grey70", expand=False))
        console.print(table)


class PullDatasetCMD(CMD):
    """ Download a dataset """
    COMMAND = "pull"
    NAMESPACE = "datasets"

    def init_parser(self, parser: argparse.ArgumentParser):
        parser.add_argument('name')
        parser.add_argument('-u', '--skip-verification', action='store_true', help="Skip archive verification")
        parser.add_argument('-q', '--quiet', action='store_true', help='Suppress download info output')

    def run(self, argv: argparse.Namespace):
        # update repo index if necessary
        if check_update_repo_index():
            update_repo_index()

        datasets_dir = DatasetsDir.load()
        dataset = datasets_dir.get(argv.name, cls=Dataset)
        dataset.pull(quiet=argv.quiet, show_progress=True, verify=not argv.skip_verification)


class ImportDatasetCMD(CMD):
    """ Import a dataset from a zip file """
    COMMAND = "import"
    NAMESPACE = "datasets"

    def init_parser(self, parser: argparse.ArgumentParser):
        parser.add_argument('zip_file')
        parser.add_argument('-u', '--skip-verification', action='store_true',
                            help='Do not check hash in repo index.')
        parser.add_argument('-q', '--quiet', action='store_true',
                            help='Suppress download info output')

    def run(self, argv: argparse.Namespace):
        datasets_dir = DatasetsDir.load()
        archive = Path(argv.zip_file)
        std_out = console
        if argv.quiet:
            std_out = void_console

        if not archive.is_file() and archive.suffix != '.zip':
            error_console.print(f'Given archive ({archive}) does not exist or is not a valid zip archive !!!')
            sys.exit(1)

        if not argv.skip_verification:
            with std_out.status(f'Hashing {archive.name}'):
                md5hash = md5sum(archive)
            item = datasets_dir.find_by_hash(md5hash)

            if item is None:
                error_console.print(f'Archive {archive.name} does not correspond to a registered dataset')
                sys.exit(1)
            name = item.name
            std_out.print(f"[green]Dataset {name} detected")
        else:
            name = archive.stem
            warning_console.print(f"Importing {name} without checking, could be naming/file mismatch")

        # unzip dataset
        with std_out.status(f"Unzipping {name}..."):
            extract(archive, datasets_dir.root_dir / name)

        std_out.print(f"[green]Dataset {name} installed successfully !!")


class RemoveDatasetCMD(CMD):
    """ Remove a dataset item """
    COMMAND = "rm"
    NAMESPACE = "datasets"

    def init_parser(self, parser: argparse.ArgumentParser):
        parser.add_argument('name')

    def run(self, argv: argparse.Namespace):
        dataset_dir = DatasetsDir.load()
        dts = dataset_dir.get(argv.name)
        if dts:
            dts.uninstall()
            console.log("[green] Dataset uninstalled successfully !")
        else:
            error_console.log(f"Failed to find dataset named :{argv.name}")
