import argparse
import sys
from pathlib import Path

from rich.padding import Padding
from rich.table import Table

from zerospeech.generics import checkpoints
from zerospeech.misc import md5sum, extract
from zerospeech.networkio import check_update_repo_index, update_repo_index
from zerospeech.out import console, error_console, void_console, warning_console
from zerospeech.settings import get_settings
from .cli_lib import CMD

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

        chkpt_dir = checkpoints.CheckpointDir.load()
        chkpt = chkpt_dir.get(argv.name, cls=checkpoints.CheckPointItem)
        chkpt.pull(quiet=argv.quiet, show_progress=True, verify=not argv.skip_verification)


class ImportCheckpointCMD(CMD):
    """ Import checkpoints from a zip archive """
    COMMAND = "import"
    NAMESPACE = "checkpoints"

    def init_parser(self, parser: argparse.ArgumentParser):
        parser.add_argument("zip_file")
        parser.add_argument('-u', '--skip-verification', action='store_true',
                            help='Do not check hash in repo index.')
        parser.add_argument('-q', '--quiet', action='store_true',
                            help='Suppress download info output')

    def run(self, argv: argparse.Namespace):
        # update repo index if necessary
        if check_update_repo_index():
            update_repo_index()

        chkpt_dir = checkpoints.CheckpointDir.load()
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
            item = chkpt_dir.find_by_hash(md5hash)
            if item is None:
                error_console.print(f'Archive {archive.name} does not correspond to a registered checkpoint archive')
                sys.exit(1)
            name = item.name
            std_out.print(f"[green]Checkpoint {name} detected")
        else:
            name = archive.stem
            warning_console.print(f"Importing {name} without checking, could be naming/file mismatch")

        with std_out.status(f"Unzipping {name}..."):
            extract(archive, chkpt_dir.root_dir / name)

        std_out.print(f"[green]Checkpoint {name} installed successfully !!")


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
