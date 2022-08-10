import enum
import re
from pathlib import Path
from zipfile import ZipFile

from Crypto.Hash import MD5


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
