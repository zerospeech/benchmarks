from pathlib import Path
from typing import Optional, Any

from pydantic import BaseModel, AnyUrl, parse_raw_as, AnyHttpUrl

from ..misc import load_obj
from .leaderboard import PublicationEntry


class PublicationInfo(BaseModel):
    author_label: str = ""
    authors: str
    paper_title: Optional[str]
    paper_url: Optional[str]
    publication_year: int
    bib_reference: Optional[str]
    DOI: Optional[str]
    institution: str
    team: Optional[str]


class ModelInfo(BaseModel):
    model_id: Optional[str]
    system_description: str
    train_set: str
    gpu_budget: Optional[str]
    parameters: Optional[Any]


class MetaFile(BaseModel):
    username: Optional[str]
    model_info: ModelInfo
    publication: PublicationInfo
    open_source: bool
    code_url: Optional[AnyUrl]

    @classmethod
    def from_file(cls, file: Path, enforce: bool = False):
        if not file.is_file() and not enforce:
            return None
        return cls.parse_obj(load_obj(file))

    def get_publication_info(self) -> PublicationEntry:
        pub = self.publication

        return PublicationEntry(
            author_short=pub.author_label,
            authors=pub.authors,
            paper_title=pub.paper_title,
            paper_ref=f"{pub.authors} ({pub.publication_year} {pub.paper_title})",
            bib_ref=pub.bib_reference,
            paper_url=parse_raw_as(AnyHttpUrl, pub.paper_url),
            pub_year=pub.publication_year,
            team_name=pub.team,
            institution=pub.institution,
            code=self.code_url,
            DOI=pub.DOI,
            open_science=self.open_source
        )
