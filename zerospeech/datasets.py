import json
from pathlib import Path
from typing import Optional, Dict, Generic, TypeVar, ClassVar, Type

from pydantic import BaseModel, validator, Field

from .data_items import Item, ItemType, FileListItem, FileItem
from .misc import download_extract_zip
from .out import console
from .repository import DownloadableItemDir, DownloadableItem
from .settings import get_settings

st = get_settings()

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


class Dataset(DownloadableItem):
    """ Generic definition of a dataset """
    key_name: ClassVar[str] = "dataset"
    index: Optional[DatasetIndex] = None

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

    def pull(self, *, verify: bool = True, quiet: bool = False, show_progress: bool = False):
        """ Pull a dataset from remote to the local repository."""
        md5_hash = ""
        if verify:
            md5_hash = self.origin.md5sum

        # download & extract archive
        download_extract_zip(self.origin.zip_url, self.location, int(self.origin.total_size),
                             filename=self.name, md5sum_hash=md5_hash, quiet=quiet, show_progress=show_progress)
        if not quiet:
            console.print(f"[green]Dataset {self.name} installed successfully !!")


class DatasetsDir(DownloadableItemDir):
    """ Dataset directory manager """
    item_type: Type[DownloadableItem] = Dataset

    @classmethod
    def load(cls):
        return cls(root_dir=st.dataset_path)
