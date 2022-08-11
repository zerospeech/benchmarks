import json
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict, Generic, TypeVar, Type

import requests
from pydantic import BaseModel, DirectoryPath, AnyHttpUrl, validator, parse_obj_as, Field

from .data_items import Item, ItemType, FileListItem, FileItem
from .misc import md5sum, unzip, SizeUnit
from .out import with_progress, console
from .settings import get_settings

st = get_settings()


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

    @classmethod
    def load(cls):
        """ Load index from disk """
        with st.repository_index.open() as fp:
            data = json.load(fp)
        return cls(**data)


T = TypeVar("T")


class Namespace(Generic[T]):
    """Simple object for storing attributes.

    Implements equality by attribute names and values, and provides a simple
    string representation.
    """

    def __init__(self, data: Dict[str, T]):
        # self._store: Dict[str, T] = {}
        for name in data:
            setattr(self, name, data[name])


class Subset(BaseModel):
    """ A subset of a dataset containing various items."""
    items_dict: Dict[str, Item]

    @validator("items_dict", pre=True)
    def items_parse(cls, values):
        """ Allow items to be cast to the correct subclass """
        casted_items = dict()
        for k, v, in values.items():
            item_type = ItemType(v.get('item_type', "base_item"))
            if item_type == ItemType.filelist_item:
                casted_items[k] = FileListItem.parse_obj(v)
            elif item_type == ItemType.file_item:
                casted_items[k] = FileItem.parse_obj(v)
            else:
                v["item_type"] = item_type
                casted_items[k] = Item(**v)

        return casted_items

    @property
    def items(self) -> Namespace[Item]:
        return Namespace[Item](self.items_dict)

    def make_relative(self, relative_to: Path):
        """ Convert all the items to relative paths """
        for _, item in self.items_dict.items():
            item.relative_to(relative_to)

    def make_absolute(self, root_dir: Path):
        """ Convert all items to absolute paths """
        for _, item in self.items_dict.items():
            item.absolute_to(root_dir)


class DatasetIndex(BaseModel):
    """ A metadata object indexing all items in a dataset."""
    root_dir: Path
    subsets_dict: Dict[str, Subset] = Field(default_factory=dict)

    @property
    def subsets(self) -> Namespace[Subset]:
        return Namespace[Subset](self.subsets_dict)

    def make_relative(self):
        """ Convert all the subsets to relative paths """
        for _, item in self.subsets_dict.items():
            item.make_relative(self.root_dir)

    def make_absolute(self):
        """ Convert all the subsets to absolute paths """
        for _, item in self.subsets_dict.items():
            item.make_absolute(self.root_dir)


class Dataset(BaseModel):
    """ Generic definition of a dataset """
    location: Path
    origin: RepositoryItem
    index: Optional[DatasetIndex] = None

    @property
    def installed(self) -> bool:
        return self.location.is_dir()

    @property
    def name(self) -> str:
        return self.origin.name

    @property
    def index_path(self):
        """ Path to the index file """
        p = self.location / 'index.json'
        if not p.is_file():
            raise ValueError(f'Dataset {self.origin.name} has no build-in index file')
        return p

    def load_index(self):
        """ Load the dataset index """
        with self.index_path.open() as fp:
            self.index = DatasetIndex(root_dir=self.location, **json.load(fp))

    def pull(self, *, verify: bool = True, show_progress: bool = False):
        """ Pull a dataset from remote to the local repository."""
        tmp_dir = st.mkdtemp()
        response = requests.get(self.origin.zip_url, stream=True)

        with with_progress(show=show_progress, file_transfer=True) as progress:
            total = int(self.origin.total_size)
            task1 = progress.add_task(f"[red]Downloading {self.location.name}...", total=total)

            with (tmp_dir / f"{self.origin.name}.zip").open("wb") as stream:
                for chunk in response.iter_content(chunk_size=1024):
                    stream.write(chunk)
                    progress.update(task1, advance=1024)

            progress.update(task1, completed=total, visible=False)
            console.print("[green]Download completed Successfully!")

        with with_progress(show=show_progress) as progress:
            task2 = progress.add_task(f"[red]Verifying md5sum from repository...", total=None, visible=False)
            task3 = progress.add_task(f"[red]Unzipping archive...", total=None, visible=False)

            if verify:
                progress.update(task2, visible=True)
                h = md5sum(tmp_dir / f"{self.origin.name}.zip")

                if h == self.origin.md5sum:
                    console.print("[green]MD5 sum verified!")
                else:
                    console.print("[green]MD5sum Failed, Check with repository administrator.\nExiting...")
                    sys.exit(1)
                progress.update(task2, visible=False)

            progress.update(task3, visible=True)
            unzip(tmp_dir / f"{self.origin.name}.zip", self.location)
            progress.update(task3, visible=False)
            console.print(f"[green]Dataset {self.name} installed successfully !!")


class DatasetsDir(BaseModel):
    root_dir: DirectoryPath

    @classmethod
    def load(cls):
        return cls(root_dir=st.dataset_path)

    @property
    def datasets(self) -> List[str]:
        """ Returns a list of installed datasets """
        return [d.name for d in self.root_dir.iterdir() if d.is_dir()]

    @property
    def available_datasets(self) -> List[str]:
        """ Return a list of available_datasets """
        index = RepositoryIndex.load()
        return [d.name for d in index.datasets]

    @staticmethod
    def find_repository(dataset_name: str) -> Optional[RepositoryItem]:
        index = RepositoryIndex.load()
        for d in index.datasets:
            if d.name == dataset_name:
                return d
        return None

    def get(self, name, cls: Type[Dataset] = Dataset) -> Optional[Dataset]:
        loc = self.root_dir / name
        repo = self.find_repository(name)
        if repo is None:
            return None
        return cls(location=loc, origin=repo)
