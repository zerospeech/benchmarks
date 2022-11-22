import json
from pathlib import Path
from typing import Optional, Dict, Generic, TypeVar, ClassVar, Type, Any, Union

from pydantic import BaseModel, validator, Field
from pydantic.generics import GenericModel

from .data_items import Item, ItemType, FileListItem, FileItem
from .repository import RepoItemDir, ImportableItem, DownloadableItem, InstallConfig
from ..misc import download_extract_zip, load_obj, download_file
from ..out import console
from ..settings import get_settings

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
        """ Get Store as dict """
        return self.store

    def get(self, name: str, default: Any = None):
        """ Access items by name """
        return self.store.get(name, default)

    def __getattr__(self, name) -> Optional[T]:
        """ Reimplementation of getattr """
        a: T = self.store.get(name, None)
        return a

    def __iter__(self):
        """ Allow to iterate over store """
        return iter(self.store.items())


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

    @validator("subsets", pre=True)
    def subsets_parse(cls, values):
        return Namespace[Subset](store=values)

    def make_relative(self):
        """ Convert all the subsets to relative paths """
        for _, item in self.subsets:
            item.make_relative(self.root_dir)

    def make_absolute(self):
        """ Convert all the subsets to absolute paths """
        for _, item in self.subsets:
            item.make_absolute(self.root_dir)


class Dataset(DownloadableItem, ImportableItem):
    """ Generic definition of a dataset """
    key_name: ClassVar[str] = "datasets"
    index: Optional[DatasetIndex] = None

    @property
    def name(self) -> str:
        """ Returns the dataset name """
        return getattr(self, "__dataset_name__", '')

    def is_external(self) -> bool:
        """ Returns true if the dataset is external """
        return self.origin.type == "external"

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
        if self.origin.type == "external":
            raise ValueError("External datasets cannot be pulled from the repository !!")

        md5_hash = ""
        if verify:
            md5_hash = self.origin.md5sum

        # download & extract archive
        download_extract_zip(self.origin.zip_url, self.location, int(self.origin.total_size),
                             filename=self.name, md5sum_hash=md5_hash, quiet=quiet, show_progress=show_progress)
        if not quiet:
            console.print(f"[green]Dataset {self.name} installed successfully !!")

    def import_(self, *, location: Path, verify: bool = True, quiet: bool = False, show_progress: bool = False):
        """ Import dataset from a directory """
        # todo: add informational prints
        if self.origin.type == "Internal":
            raise ValueError("internal datasets cannot be imported")

        # 1) verify location is valid
        if not location.is_dir():
            raise ValueError(f'Cannot import from {location} as its not a valid location')

        # 2) create target dir
        self.location.mkdir(exist_ok=True, parents=True)

        # 3) download & load configuration file
        download_file(url=self.origin.install_config, dest=(self.location / "install_config.json"))
        install_config = InstallConfig.parse_obj(load_obj(self.location / "install_config.json"))
        # 4) Perform installation actions
        for _, rule in sorted(install_config.rules.items()):
            if rule.action == 'download':
                target = self.location / rule.target
                target.parent.mkdir(exist_ok=True, parents=True)
                download_file(url=rule.source, dest=target)
            elif rule.action == 'symlink':
                for src, tgt in rule.source_target:
                    file = self.location / src
                    file.parent.mkdir(exist_ok=True)
                    file.symlink_to(location / tgt)
            elif rule.action == 'download_extract':
                download_extract_zip(
                    zip_url=rule.source, target_location=(self.location / rule.target),
                    size_in_bytes=int(rule.source_size), quiet=quiet, show_progress=show_progress
                )
            else:
                raise ValueError(f'Unknown action {rule.action}')

        # 5) export index from config file
        with self.index_path.open('w') as fp:
            json.dump(install_config.index_obj, fp)


class DatasetsDir(RepoItemDir):
    """ Dataset directory manager """
    item_type: ClassVar[Union[Type[DownloadableItem], Type[ImportableItem]]] = Dataset

    @classmethod
    def load(cls):
        return cls(root_dir=st.dataset_path)
