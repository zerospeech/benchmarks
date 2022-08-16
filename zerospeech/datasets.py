import json
from pathlib import Path
from typing import Optional, Dict, Generic, TypeVar, ClassVar, Type

from pydantic import BaseModel, validator, Field
from pydantic.generics import GenericModel

from .data_items import Item, ItemType, FileListItem, FileItem
from .misc import download_extract_zip
from .out import console
from .repository import DownloadableItemDir, DownloadableItem
from .settings import get_settings

st = get_settings()

T = TypeVar("T")


class DatasetNotInstalledError(Exception):
    """ Exception used for a non locally installed dataset """
    pass


class DatasetNotFoundError(Exception):
    """ Exception used for a non available dataset """
    pass


class Namespace(GenericModel, Generic[T]):
    """ Simple object for storing attributes. """
    store: Dict[str, T] = Field(default_factory=dict)

    @property
    def as_dict(self) -> Dict[str, T]:
        return self.store

    def __getattr__(self, name) -> Optional[T]:
        a: T = self.store.get(name, None)
        return a

    def __iter__(self):
        return self.store.items()


class Subset(BaseModel):
    """ A subset of a dataset containing various items."""
    items: Namespace[Item]

    @validator("items", pre=True)
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

        return Namespace[Item](store=casted_items)

    def make_relative(self, relative_to: Path):
        """ Convert all the items to relative paths """
        for _, item in self.items:
            item.relative_to(relative_to)

    def make_absolute(self, root_dir: Path):
        """ Convert all items to absolute paths """
        for _, item in self.items:
            item.absolute_to(root_dir)


class DatasetIndex(BaseModel):
    """ A metadata object indexing all items in a dataset."""
    root_dir: Path
    subsets: Namespace[Subset]

    def make_relative(self):
        """ Convert all the subsets to relative paths """
        for _, item in self.subsets:
            item.make_relative(self.root_dir)

    def make_absolute(self):
        """ Convert all the subsets to absolute paths """
        for _, item in self.subsets:
            item.make_absolute(self.root_dir)


class Dataset(DownloadableItem):
    """ Generic definition of a dataset """
    key_name: ClassVar[str] = "datasets"
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
