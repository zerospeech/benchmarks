import argparse

from rich.padding import Padding
from rich.table import Table

from .cli_lib import CMD
from ..model import checkpoints
from ..networkio import check_update_repo_index, update_repo_index
from ..out import console, error_console
from ..settings import get_settings

st = get_settings()


class CheckpointsCMD(CMD):
    """Manipulate Checkpoints """
    COMMAND = "checkpoints"
    NAMESPACE = ""

    def init_parser(self, parser: argparse.ArgumentParser):
        parser.add_argument("--local", action="store_true", help="List local checkpoint only")

    def run(self, argv: argparse.Namespace):
        checkpoints_dir = checkpoints.CheckpointDir.load()
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Name")
        table.add_column("Origin")
        table.add_column("Size")
        table.add_column("Installed")

        if argv.local:
            dt_list = checkpoints_dir.items
        else:
            dt_list = checkpoints_dir.available_items

        for d in dt_list:
            dts = checkpoints_dir.get(d)
            if dts.origin.type == 'internal':
                host = st.repo_origin.host
            else:
                host = "external"

            table.add_row(
                dts.name, host, dts.origin.size_label, f"{dts.installed}"
            )

        console.print(
            Padding(f"==> RootDir: {checkpoints_dir.root_dir}", (1, 0, 1, 0), style="bold grey70", expand=False))
        console.print(table)


class PullCheckpointCMD(CMD):
    """ Download a checkpoint item """
    COMMAND = "pull"
    NAMESPACE = "checkpoints"

    def init_parser(self, parser: argparse.ArgumentParser):
        parser.add_argument('name')
        parser.add_argument('-u', '--skip-verification', action='store_true', help="Skip archive verification")
        parser.add_argument('-q', '--quiet', action='store_true', help='Suppress download info output')

    def run(self, argv: argparse.Namespace):
        # update repo index if necessary
        if check_update_repo_index():
            update_repo_index()

        datasets = checkpoints.CheckpointDir.load()
        dataset = datasets.get(argv.name, cls=checkpoints.CheckPointItem)
        dataset.pull(quiet=argv.quiet, show_progress=True, verify=not argv.skip_verification)


class RemoveCheckpointCMD(CMD):
    """ Remove a checkpoint item """
    COMMAND = "rm"
    NAMESPACE = "checkpoints"

    def init_parser(self, parser: argparse.ArgumentParser):
        parser.add_argument('name')

    def run(self, argv: argparse.Namespace):
        checkpoints_dir = checkpoints.CheckpointDir.load()
        cpt = checkpoints_dir.get(argv.name)
        if cpt:
            cpt.uninstall()
            console.log("[green] Checkpoint uninstalled successfully !")
        else:
            error_console.log(f"Failed to find checkpoint named :{argv.name}")
