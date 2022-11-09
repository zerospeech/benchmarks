import contextlib
import enum
import io
import json
import sys
from pathlib import Path
from typing import Dict, List, Union
from zipfile import ZipFile

import humanize
# from datasize import DataSize todo: find out why this was deleted ? maybe on unpushed thing on laptop?
from pydantic import ByteSize, BaseModel
import requests
from Crypto.Hash import MD5  # noqa: the package name is not the same

try:
    import yaml
except ImportError:
    yaml = None
try:
    import tomli # noqa: is not a strict requirement
except ImportError:
    tomli = None

from .out import with_progress, void_console, console
from .settings import get_settings

st = get_settings()


class SizeUnit(BaseModel):
    __root__: ByteSize

    @property
    def human_readable(self):
        return self.__root__.human_readable(decimal=True)

    @property
    def as_bytes(self):
        return self.__root__

# todo: see if i can remove this from the codebase ?
# todo can we remove humanize from requirements ? or is it still used ?
# class SizeUnit(enum.Enum):
#     BYTES = 1
#     KB = 2
#     MB = 3
#     GB = 4
#
#     @staticmethod
#     def get_unit(text):
#         """ Check contents of text to find units of measurement"""
#
#         if any(x in text for x in ("KB", "Ko", "K")):
#             return SizeUnit.KB
#         elif any(x in text for x in ("MB", "Mo", "M")):
#             return SizeUnit.MB
#         elif any(x in text for x in ("GB", "Go", "G")):
#             return SizeUnit.GB
#         else:
#             return SizeUnit.BYTES
#
#     @staticmethod
#     def convert_to_bytes(size_with_unit: str) -> float:
#         # todo: replace this ??
#         #: DataSize(size_with_unit.replace(' ', ''))
#         return float("123.532")
#
#     @staticmethod
#     def fmt(num: Union[int, float]) -> str:
#         return humanize.naturalsize(num).replace(' ', '')


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


def symlink_dir_contents(source: Path, dest: Path):
    """ create symlinks of all content in a directory into another """
    dest.mkdir(exist_ok=True, parents=True)
    for item in source.iterdir():
        (dest / item.name).symlink_to(item, target_is_directory=item.is_dir())


def download_file(url: str, dest: Path):
    """ Download a file from a given URL """
    response = requests.get(url, allow_redirects=True)
    with dest.open('wb') as fb:
        fb.write(response.content)


@contextlib.contextmanager
def nostdout():
    """ Redirect stdout to /dev/null """
    save_stdout = sys.stdout
    sys.stdout = io.BytesIO()
    yield
    sys.stdout = save_stdout

