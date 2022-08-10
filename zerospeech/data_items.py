import abc

from pydantic import BaseModel


class FileTypes(str, Enum):
    txt = "txt"
    npy = "npy"
    csv = "csv"
    wav = "wav"


class Item(BaseModel, abc.ABC):
    """ The Atom of the dataset an item can be a file list, a file or a datastructure """
    pass


class FileListItem(Item):
    file_type: FileTypes
    file_list: List[Path]


class FileItem(Item):
    file_type: FileTypes
    file: Path
