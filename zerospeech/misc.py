import _thread as thread
import contextlib
import io
import json
import os
import re
import shutil
import subprocess
import sys
import tarfile
import threading
import urllib.parse
from pathlib import Path
from typing import Dict, List, Union, Optional, Protocol, TYPE_CHECKING
from zipfile import ZipFile

import requests
from Crypto.Hash import MD5  # noqa: the package name is not the same
# from datasize import DataSize todo: find out why this was deleted ? maybe on unpushed thing on laptop?
from pydantic import ByteSize, BaseModel

if TYPE_CHECKING:
    pass

try:
    import pycurl
    import certifi
except ImportError:
    pycurl = None
    certifi = None

try:
    import yaml
except ImportError:
    yaml = None
try:
    import tomli  # noqa: is not a strict requirement
except ImportError:
    tomli = None

from .out import with_progress, void_console, console
from .settings import get_settings

st = get_settings()


def exit_after(s):
    """ Decorator that kills function after s number of seconds
    Usage:

        @exit_after(10)
        def f():
            # complex computation


        try:
            f()
        except KeyboardInterrupt:
            print('Function f could not finish in 10 seconds and was interrupted')

    """

    def process_quit():
        """ Raise a Keyboard interrupt"""
        thread.interrupt_main()  # raises KeyboardInterrupt

    def outer(fn):
        def inner(*args, **kwargs):
            """
            Uses a timer from threading module to raise a KeyboardInterrupt after s seconds.
            """
            timer = threading.Timer(s, process_quit)
            timer.start()
            try:
                result = fn(*args, **kwargs)
            finally:
                """ Cancel timer if function finished processing """
                timer.cancel()
            return result

        return inner

    return outer


class ContextualItem(Protocol):
    """ Item providing context to exceptions """

    def print(self, allow_warnings: bool = False):
        """ protocol function allowing to print context """
        pass


class ContextualException(Exception):
    """ Custom exception providing a context """

    def __init__(self, msg: str, ctx: Optional[ContextualItem] = None):
        self._context: ContextualItem = ctx
        super().__init__(msg)

    def print_context(self, allow_warnings: bool = False):
        """ Prints the current context """
        if self._context:
            self._context.print(allow_warnings)


class ScoresNotFound(ContextualException):
    pass


class MetaYamlNotValid(ContextualException):
    pass


class InvalidSubmissionError(ContextualException):
    pass


class SizeUnit(BaseModel):
    __root__: ByteSize

    @property
    def human_readable(self):
        return self.__root__.human_readable(decimal=True)

    @property
    def as_bytes(self):
        return self.__root__


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


def untar(archive: Path, output: Path):
    """ Extract a tar archive (supports gzipped format) into the output directory"""
    # create folder if it does not exist
    output.mkdir(exist_ok=True, parents=True)
    # Open & extract
    with tarfile.open(archive, 'r') as tar:
        tar.extractall(path=output)


def extract(archive: Path, output: Path):
    """ Extract an archive into the output directory """
    if archive.suffix in ('.zip',):
        unzip(archive, output)
    elif archive.suffix in ('.tar', '.gz', '.tgz', '.bz2', '.tbz2', '.xz', '.txz'):
        untar(archive, output)
    else:
        raise ValueError(f'{archive.suffix}: Unsupported archive format')


def zip_folder(archive_file: Path, location: Path):
    """ Create a zip archive from a folder """
    with ZipFile(archive_file, 'w') as zip_obj:
        for file in filter(lambda x: x.is_file(), location.rglob("*")):
            zip_obj.write(file, str(file.relative_to(location)))


def get_request_filename(response: requests.Response) -> str:
    """ Get filename from response """
    if "Content-Disposition" in response.headers.keys():
        return re.findall("filename=(.+)", response.headers["Content-Disposition"])[0]
    else:
        return Path(urllib.parse.unquote(response.url)).name


def _download_file_requests(url: str, target: Path, size_in_bytes: int, *, show_progress: bool = True):
    """" Download a file from url using requests library """
    response = requests.get(url, stream=True)

    with with_progress(show=show_progress, file_transfer=True) as progress:
        total = int(size_in_bytes)
        task1 = progress.add_task(f"[red]Downloading {target.name}...", total=total)

        with target.open("wb") as stream:
            for chunk in response.iter_content(chunk_size=1024):
                stream.write(chunk)
                progress.update(task1, advance=1024)
        progress.update(task1, completed=total, visible=False)


def _download_file_curl(url: str, target: Path, size_in_bytes: int, *, show_progress: bool = True):
    """ Download a file from url using libcurl library (either as binding or as subprocess) """
    if None in (pycurl, certifi):
        if shutil.which('curl') is None:
            raise OSError('curl download backend is not available.')
        # Use subprocess
        if show_progress:
            cmd = f"{shutil.which('curl')} --retry 7 -o {target} {url}"
        else:
            cmd = f"{shutil.which('curl')} --retry 7 --silent -S -o {target} {url}"

        # Run as subprocess command
        subprocess.run(cmd, shell=True, check=True)
    else:
        with with_progress(show=show_progress, file_transfer=True) as progress:
            total = int(size_in_bytes)
            task1 = progress.add_task(f"[red]Downloading {target.name}...", total=total)
            total_dl_d = [0]

            def status(download_t, download_d: int, upload_t, upload_d, total=total_dl_d):
                progress.update(task1, advance=download_d - total[0])
                # update the total dl'd amount
                total[0] = download_d

            with target.open("wb") as buffer:
                c = pycurl.Curl()
                c.setopt(c.URL, url)
                c.setopt(c.WRITEDATA, buffer)
                c.setopt(c.CAINFO, certifi.where())
                # follow redirects:
                c.setopt(c.FOLLOWLOCATION, True)
                # custom progress bar
                c.setopt(c.NOPROGRESS, False)
                c.setopt(c.XFERINFOFUNCTION, status)
                c.perform()
                c.close()
        print()


def _download_file_wget(url: str, target: Path, *, show_progress: bool = True):
    """ Download a file from url using wget """
    max_tries = os.environ.get("MAX_TRIES", 10)

    if shutil.which('wget') is None:
        raise OSError('wget download backend is not available.')

    if show_progress:
        cmd = f"{shutil.which('wget')} --tries={max_tries} -O {target} {url}"
    else:
        cmd = f"{shutil.which('wget')} --quiet --tries={max_tries} -O {target} {url}"

    # Run as subprocess command
    subprocess.run(cmd, shell=True, check=True)


def download_file2(url: str, target: Path, size_in_bytes: int, *, show_progress: bool = True):
    """ Download a file from url using the optimal library """
    download_backend = os.environ.get("DL_BACKEND", "wget")  # lookup backend

    try:
        if download_backend == "curl":
            _download_file_curl(url, target, size_in_bytes, show_progress=show_progress)
        elif download_backend == "requests":
            _download_file_requests(url, target, size_in_bytes, show_progress=show_progress)
        else:
            _download_file_wget(url, target, show_progress=show_progress)
    except OSError:
        # Fallback on requests if others not found
        _download_file_requests(url, target, size_in_bytes, show_progress=show_progress)


def download_extract_archive(
        archive_url: str, target_location: Path, size_in_bytes: int, *, filename: str = "",
        md5sum_hash: str = "", quiet: bool = False, show_progress: bool = True,
):
    tmp_dir = st.mkdtemp()
    tmp_filename = tmp_dir / Path(archive_url).name
    if filename:
        tmp_filename = tmp_dir / filename

    if quiet:
        _console = void_console
        show_progress = False
    else:
        _console = console

    download_file2(archive_url, tmp_filename, size_in_bytes, show_progress=show_progress)
    _console.print("[green]Download completed Successfully!")

    if md5sum_hash != "":
        with _console.status("[red]Verifying md5sum from repository..."):
            h = md5sum(tmp_filename)

        if h == md5sum_hash:
            _console.print("[green]MD5 sum verified!")
        else:
            _console.print("[green]MD5sum Failed, Check with repository administrator.\nExiting...")
            sys.exit(1)

    with _console.status("[red]Extracting archive..."):
        extract(tmp_filename, target_location)


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
