import abc
from enum import Enum
from pathlib import Path
from typing import List

from pydantic import BaseModel, validator


class FileTypes(str, Enum):
    txt = "txt"
    npy = "npy"
    csv = "csv"
    wav = "wav"
    item = "item"


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


class FileItem(Item):
    item_type: ItemType = ItemType.file_item
    file: Path

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
