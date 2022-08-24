from pathlib import Path
from typing import Optional, Any

from pydantic import BaseModel, AnyUrl

from ..misc import load_obj


class PublicationInfo(BaseModel):
    author_label: str = ""
    authors: str
    paper_title: Optional[str]
    paper_url: Optional[str]
    publication_year: int
    institution: str
    team: Optional[str]


class ModelInfo(BaseModel):
    system_description: str
    train_set: str
    gpu_budget: Optional[str]
    parameters: Optional[Any]


class MetaFile(BaseModel):
    model_info: ModelInfo
    publication: PublicationInfo
    open_source: bool
    code_url: Optional[AnyUrl]

    @classmethod
    def from_file(cls, file: Path):
        return cls.parse_obj(load_obj(file))
