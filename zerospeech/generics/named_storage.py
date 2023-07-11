from pathlib import Path
from typing import Optional, Dict, Generic, Any, TypeVar, Tuple

from pydantic import BaseModel, validator, Field
from pydantic.generics import GenericModel

from .data_items import (
    Item, ItemType, FileListItem, FileItem
)

T = TypeVar("T")


class Namespace(GenericModel, Generic[T]):
    """ Simple object for storing attributes. """
    store: Dict[str, T] = Field(default_factory=dict)

    @property
    def names(self) -> Tuple[str, ...]:
        return tuple(self.store.keys())

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

    @property
    def names(self) -> Tuple[str, ...]:
        return self.items.names

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
