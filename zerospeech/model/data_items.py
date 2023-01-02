from enum import Enum
from pathlib import Path
from typing import List, Callable, Iterator

from pydantic import BaseModel, validator


class FileTypes(str, Enum):
    txt = "txt"
    npy = "npy"
    csv = "csv"
    wav = "wav"
    flac = "flac"
    item = "item"  # abx task file
    tsv = "tsv"
    json = "json"
    yaml = "yaml"
    phn = "phn"  # phone alignment file
    wrd = "wrd"  # words alignment file

    @property
    def ext(self) -> str:
        return f".{self.value}"

    @classmethod
    def dataframe_types(cls):
        return {
            cls.csv, cls.txt, cls.tsv, cls.item
        }

    @classmethod
    def audio_types(cls):
        return {
            cls.wav, cls.flac
        }

    @classmethod
    def numpy_types(cls):
        return {
            cls.npy, cls.txt
        }


class ItemType(str, Enum):
    base_item = "base_item"
    filelist_item = "filelist_item"
    file_item = "file_item"


class Item(BaseModel):
    """ The Atom of the dataset an item can be a file list, a file or a datastructure """
    item_type: ItemType = ItemType.base_item
    file_type: FileTypes
    relative_path: bool

    @validator('file_type', pre=True)
    def fix_file_extension(cls, v):
        if isinstance(v, str):
            return v.replace('.', '')
        return v

    def relative_to(self, path: Path):
        """ Convert internal path to relative paths """
        self.relative_path = True

    def absolute_to(self, path: Path):
        self.relative_path = False

    class Config:
        extra = "allow"


class FileListItem(Item):
    item_type: ItemType = ItemType.filelist_item
    files_list: List[Path]

    @classmethod
    def from_dir(cls, path: Path, f_type: FileTypes):
        """ Build a FileListItem from a directory"""

        temp = path
        rgexp = f"*{f_type.ext}"
        thing = temp.rglob(rgexp)
        file_list = list(thing)

        return cls(
            file_type=f_type,
            files_list=file_list,
            relative_path=False
        )

    def __iter__(self) -> Iterator[Path]:
        return iter(self.files_list)

    def relative_to(self, path: Path):
        """ Convert all paths to relative if they are absolute """
        if not self.relative_path:
            for i in range(len(self.files_list)):
                self.files_list[i] = self.files_list[i].relative_to(path)
        # call method in super class
        super(FileListItem, self).relative_to(path)

    def absolute_to(self, path: Path):
        """ Convert all paths to absolute if they are relative """
        if self.relative_path:
            for i in range(len(self.files_list)):
                self.files_list[i] = path / self.files_list[i]
        # call method in super class
        super(FileListItem, self).absolute_to(path)

    class Config:
        extra = "ignore"


FileValidator = Callable[["FileItem"], bool]


class FileItem(Item):
    item_type: ItemType = ItemType.file_item
    file: Path

    @classmethod
    def from_file(cls, path: Path, relative: bool = False):
        """ Build a FileItem from a path """
        suffix = path.suffix.replace('.', '')
        return cls(
            file=path,
            file_type=FileTypes(suffix),
            relative_path=relative
        )

    def valid(self, validate: FileValidator) -> bool:
        # todo rethink a bit this validation pattern
        return self.file.resolve().is_file() and validate(self)

    def relative_to(self, path: Path):
        """ Convert all paths to relative if they are absolute """
        if not self.relative_path:
            self.file = self.file.relative_to(path)

        # call method in super class
        super(FileItem, self).relative_to(path)

    def absolute_to(self, path: Path):
        """ Convert all paths to absolute if they are relative """
        if self.relative_path:
            self.file = path / self.file

        # call method in super class
        super(FileItem, self).absolute_to(path)

    class Config:
        extra = "ignore"
