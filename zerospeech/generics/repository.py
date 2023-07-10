import abc
import functools
import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Type, ClassVar, Literal, Union, Tuple, Dict, Any

from pydantic import BaseModel, AnyHttpUrl, validator, parse_obj_as, DirectoryPath, ByteSize, root_validator

from ..settings import get_settings

st = get_settings()

RepositoryItemType = Literal[
    'datasets', 'samples', 'checkpoints', 'origin_item', 'downloadable_item', 'importable_item']
ItemType = Literal['internal', 'external']
InstallAction = Literal['download', 'symlink', 'download_extract']


class RepositoryItem(BaseModel):
    """ An item represents a dataset inside the repository that can be pulled locally """
    name: str
    type: ItemType
    zip_url: Optional[AnyHttpUrl]
    zip_parts: Optional[List[AnyHttpUrl]]
    install_config: Optional[AnyHttpUrl]
    md5sum: str
    total_size: ByteSize
    details_url: Optional[AnyHttpUrl]
    description: Optional[str]

    @property
    def origin_host(self) -> str:
        return self.zip_url.host

    @property
    def size_label(self) -> str:
        return self.total_size.human_readable(decimal=True)

    @validator('zip_url', pre=True)
    def cast_url1(cls, v):
        """ Cast strings to AnyHttpUrl """
        if isinstance(v, str):
            return parse_obj_as(AnyHttpUrl, v)
        return v

    @validator('zip_parts', pre=True)
    def cast_url2(cls, v):
        """ Cast strings to AnyHttpUrl """
        if isinstance(v, str):
            return parse_obj_as(AnyHttpUrl, v)
        return v

    @root_validator(pre=True)
    def validate_type(cls, values):
        valid_types = ('internal', 'external')
        current_type = values.get('type', 'internal')
        values['type'] = current_type
        assert current_type in valid_types, f'Type should be one of the following {valid_types}'

        if current_type == 'internal':
            assert values.get('zip_url') is not None \
                   or values.get('zip_parts') is not None, \
                   "Internal Items must have either a zip_url or a zip_parts value."
        elif values.get('type') == 'external':
            assert values.get('install_config') is not None, "External items must have an install_config field"
        return values


class RepositoryIndex(BaseModel):
    """ Item Indexing all datasets available online various repositories."""
    last_modified: datetime
    datasets: List[RepositoryItem]
    checkpoints: List[RepositoryItem]
    samples: List[RepositoryItem]

    @classmethod
    @functools.lru_cache
    def load(cls):
        """ Load index from disk """
        with st.repository_index.open() as fp:
            data = json.load(fp)
        return cls(**data)


class InstallRule(BaseModel):
    action: InstallAction
    source: Optional[AnyHttpUrl]
    target: Optional[str]
    source_target: Optional[List[Tuple[str, str]]]
    source_size: Optional[ByteSize]

    @root_validator(pre=True)
    def validate_actions(cls, values):
        actions = ('download', 'symlink', 'download_extract')
        if values['action'] == 'download':
            assert values.get('source') is not None, "Download action requires a source"
            assert values.get('target') is not None, "Download action requires a target"
        elif values['action'] == 'symlink':
            assert values.get('source_target') is not None, "Symlink action requires a source_target"
        elif values['action'] == 'download_extract':
            assert values.get('source') is not None, "Download_Extract action requires a source"
            assert values.get('target') is not None, "Download_Extract action requires a target"
            assert values.get('source_size') is not None, "Download_Extract action requires a source_size"
        else:
            assert values['action'] in actions, \
                f"Action needs to be one of the following {actions}"


class InstallConfig(BaseModel):
    rules: Dict[str, InstallRule]
    index_obj: Dict[str, Any]


class OriginItem(BaseModel, abc.ABC):
    """ An item that has an external origin derived from the repository """
    key_name: ClassVar[RepositoryItemType] = "origin_item"
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


class DownloadableItem(OriginItem, abc.ABC):
    """ Abstract class to define an item that can be downloaded from the repository """

    @abc.abstractmethod
    def pull(self, *, verify: bool = True, quiet: bool = False, show_progress: bool = False):
        """ Pull item from origin """
        pass


class ImportableItem(OriginItem, abc.ABC):
    """Abstract class to define item that can be imported from a local resource """

    @abc.abstractmethod
    def import_(self, location: Path, *, verify: bool = True, quiet: bool = False, show_progress: bool = False):
        """Import items from source material located locally """
        pass


class RepoItemDir(BaseModel, abc.ABC):
    """ Abstract class defining a directory manager for repository items of a specific type """
    root_dir: DirectoryPath
    item_type: ClassVar[Union[Type[DownloadableItem], Type[ImportableItem]]]

    @classmethod
    @abc.abstractmethod
    def load(cls):
        pass

    @property
    def items(self) -> List[str]:
        """ Returns a list of installed items """
        return [d.name for d in self.root_dir.iterdir() if d.is_dir()]

    @property
    def available_items(self) -> List[str]:
        index = RepositoryIndex.load()
        item_list: List[RepositoryItem] = getattr(index, self.item_type.key_name, [])
        return [d.name for d in item_list]

    def find_in_repository(self, name: str) -> Optional[RepositoryItem]:
        """Find all relevant items with the same type in repository """
        index = RepositoryIndex.load()
        item_list: List[RepositoryItem] = getattr(index, self.item_type.key_name, [])
        for d in item_list:
            if d.name == name:
                return d
        return None

    def get(self, name, cls: Union[Type[DownloadableItem], Type[ImportableItem]] = None):
        loc = self.root_dir / name
        repo = self.find_in_repository(name)
        if repo is None:
            return None

        if cls is None:
            return self.item_type(location=loc, origin=repo)
        return cls(location=loc, origin=repo)
