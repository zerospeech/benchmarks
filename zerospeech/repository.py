import abc
import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Type, ClassVar, Literal

from pydantic import BaseModel, AnyHttpUrl, validator, parse_obj_as, DirectoryPath

from .misc import SizeUnit
from .settings import get_settings

st = get_settings()


DownloadableTypes = Literal['datasets', 'samples', 'checkpoints', 'downloadable_item']


class RepositoryItem(BaseModel):
    """ An item represents a dataset inside the repository that can be pulled locally """
    name: str
    # todo see if different forms of download can be used : single zip, multi-part zip, other?
    zip_url: AnyHttpUrl
    md5sum: str
    total_size: float

    @property
    def origin_host(self) -> str:
        return self.zip_url.host

    @property
    def size_label(self) -> str:
        return SizeUnit.fmt(self.total_size)

    @validator('zip_url', pre=True)
    def cast_url(cls, v):
        """ Cast strings to AnyHttpUrl """
        if isinstance(v, str):
            return parse_obj_as(AnyHttpUrl, v)
        return v

    @validator('total_size', pre=True)
    def correct_size_format(cls, v):
        """ Converts total_size from a SIZE + UNIT string to a float representing Bytes"""
        if isinstance(v, str):
            return SizeUnit.convert_to_bytes(v)
        return v


class RepositoryIndex(BaseModel):
    """ Item Indexing all datasets available online various repositories."""
    last_modified: datetime
    datasets: List[RepositoryItem]
    checkpoints: List[RepositoryItem]
    samples: List[RepositoryItem]

    @classmethod
    def load(cls):
        """ Load index from disk """
        with st.repository_index.open() as fp:
            data = json.load(fp)
        return cls(**data)


class DownloadableItem(BaseModel, abc.ABC):
    """ Abstract class to define an item that can be downloaded from the repository """
    key_name: ClassVar[DownloadableTypes] = "downloadable_item"
    location: Path
    origin: RepositoryItem

    @property
    def installed(self) -> bool:
        """ Check if item is installed locally"""
        return self.location.is_dir()

    def uninstall(self):
        """ Uninstall item from local storage """
        shutil.rmtree(self.location)

    @property
    def name(self) -> str:
        return self.origin.name

    @abc.abstractmethod
    def pull(self, *, verify: bool = True, quiet: bool = False, show_progress: bool = False):
        pass


class DownloadableItemDir(BaseModel, abc.ABC):
    """ Abstract class defining a directory manager for DownloadableItem """
    root_dir: DirectoryPath
    item_type: Type[DownloadableItem]

    @classmethod
    @abc.abstractmethod
    def load(cls):
        pass

    @property
    def items(self) -> List[str]:
        """ Returns a list of installed datasets """
        return [d.name for d in self.root_dir.iterdir() if d.is_dir()]

    @property
    def available_items(self) -> List[str]:
        index = RepositoryIndex.load()
        item_list: List[RepositoryItem] = getattr(index, self.item_type.key_name, [])
        return [d.name for d in item_list]

    def find_in_repository(self, name: str) -> Optional[RepositoryItem]:
        index = RepositoryIndex.load()
        item_list: List[RepositoryItem] = getattr(index, self.item_type.key_name, [])
        for d in item_list:
            if d.name == name:
                return d
        return None

    def get(self, name, cls):
        loc = self.root_dir / name
        repo = self.find_in_repository(name)
        if repo is None:
            return None
        return cls(location=loc, origin=repo)
