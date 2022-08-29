import contextlib
import enum
import io
import json
import re
import sys
from pathlib import Path
from typing import Dict, List, Union
from zipfile import ZipFile

import requests
from Crypto.Hash import MD5

try:
    import yaml
except ImportError:
    yaml = None
try:
    import tomli
except ImportError:
    tomli = None

from .out import with_progress, void_console, console
from .settings import get_settings

st = get_settings()


class SizeUnit(enum.Enum):
    BYTES = 1
    KB = 2
    MB = 3
    GB = 4

    @staticmethod
    def get_unit(text):
        """ Check contents of text to find units of measurement"""

        if any(x in text for x in ("KB", "Ko", "K")):
            return SizeUnit.KB
        elif any(x in text for x in ("MB", "Mo", "M")):
            return SizeUnit.MB
        elif any(x in text for x in ("GB", "Go", "G")):
            return SizeUnit.GB
        else:
            return SizeUnit.BYTES

    @staticmethod
    def convert_unit(size_in_bytes: float, unit: "SizeUnit") -> float:
        """ Convert the size from bytes to other units like KB, MB or GB"""
        if unit == SizeUnit.KB:
            return size_in_bytes / 1024
        elif unit == SizeUnit.MB:
            return size_in_bytes / (1024 * 1024)
        elif unit == SizeUnit.GB:
            return size_in_bytes / (1024 * 1024 * 1024)
        else:
            return size_in_bytes

    @staticmethod
    def convert_to_bytes(size_with_unit: str) -> float:
        unit = SizeUnit.get_unit(size_with_unit)
        size = re.sub(r"[^0-9]", "", size_with_unit)
        size = float(size)

        if unit == SizeUnit.KB:
            return size * 1024
        elif unit == SizeUnit.MB:
            return size * (1024 * 1024)
        elif unit == SizeUnit.GB:
            return size * (1024 * 1024 * 1024)
        else:
            return size

    @staticmethod
    def fmt(num, suffix="B"):
        for unit in ["", "K", "M", "G", "T", "P", "E", "Z"]:
            if abs(num) < 1024.0:
                return f"{num:3.1f} {unit}{suffix}"
            num /= 1024.0
        return f"{num:.1f}Y{suffix}"


def load_obj(location: Path) -> Union[Dict, List]:
    """ Loads an object from standard formats (.json, yaml, ...) to a standard structure (Dict, List)"""
    with location.open() as fp, location.open('rb') as bfp:
        if location.suffix == '.json':
            return json.load(fp)
        elif yaml and location.suffix in ('.yaml', '.yml'):
            return yaml.load(fp, Loader=yaml.FullLoader)
        elif tomli and location.suffix in ('.toml', '.tml'):
            return tomli.load(bfp)
        elif location.suffix in ('.txt', '.list'):
            return fp.readlines()
        else:
            raise ValueError('File of unknown format !!')


def md5sum(file_path: Path, chunk_size: int = 8192):
    """ Return a md5 hash of a files content """
    h = MD5.new()

    with file_path.open('rb') as f:
        while True:
            chunk = f.read(chunk_size)
            if len(chunk):
                h.update(chunk)
            else:
                break
    return h.hexdigest()


def unzip(archive: Path, output: Path):
    """ Unzips contents of a zip archive into the output directory """
    # create folder if it does not exist
    output.mkdir(exist_ok=True, parents=True)
    # open & extract
    with ZipFile(archive, 'r') as zipObj:
        zipObj.extractall(output)


def zip_folder(archive_file: Path, location: Path):
    """ Create a zip archive from a folder """
    with ZipFile(archive_file, 'w') as zip_obj:
        for file in filter(lambda x: x.is_file(), location.rglob("*")):
            zip_obj.write(file, str(file.relative_to(location)))


def download_extract_zip(
        zip_url: str, target_location: Path,  size_in_bytes: int, *, filename: str = "",
        md5sum_hash: str = "", quiet: bool = False, show_progress: bool = True,
):
    tmp_dir = st.mkdtemp()
    response = requests.get(zip_url, stream=True)

    if quiet:
        _console = void_console
        show_progress = False
    else:
        _console = console

    with with_progress(show=show_progress, file_transfer=True) as progress:
        total = int(size_in_bytes)
        task1 = progress.add_task(f"[red]Downloading {filename}...", total=total)

        with (tmp_dir / f"download.zip").open("wb") as stream:
            for chunk in response.iter_content(chunk_size=1024):
                stream.write(chunk)
                progress.update(task1, advance=1024)

        progress.update(task1, completed=total, visible=False)
        _console.print("[green]Download completed Successfully!")

    # with with_progress(show=show_progress) as progress:
    #     task2 = progress.add_task(f"[red]Verifying md5sum from repository...", total=None, visible=False)
    #     task3 = progress.add_task(f"[red]Unzipping archive...", total=None, visible=False)

    if md5sum_hash != "":
        with _console.status("[red]Verifying md5sum from repository..."):
            h = md5sum(tmp_dir / f"download.zip")

        if h == md5sum_hash:
            _console.print("[green]MD5 sum verified!")
        else:
            _console.print("[green]MD5sum Failed, Check with repository administrator.\nExiting...")
            sys.exit(1)

    with _console.status("[red]Unzipping archive..."):
        unzip(tmp_dir / f"download.zip", target_location)


@contextlib.contextmanager
def nostdout():
    """ Redirect stdout to /dev/null """
    save_stdout = sys.stdout
    sys.stdout = io.BytesIO()
    yield
    sys.stdout = save_stdout
