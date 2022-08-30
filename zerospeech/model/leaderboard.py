from datetime import datetime
from enum import Enum
from typing import List, Optional, Dict, Union

from pydantic import BaseModel, AnyHttpUrl, Field


class Benchmark(str, Enum):
    ABX_15 = "ABX-15"
    ABX_17 = "ABX-17"
    ABX_LS = "ABX-LS"
    TDE_15 = "TDE-15"
    TDE_17 = "TDE-17"
    TTS0_19 = "TTS0-19"
    TTS0_LSLJ = "TTS0-LSLJ"
    sLM_21 = "sLM-21"


class ABXScoreTuple(BaseModel):
    within: Optional[float]
    across: Optional[float]


class CatScores(BaseModel):
    precision: Optional[float]
    recall: Optional[float]
    fscore: Optional[float]


class NLPScores(BaseModel):
    ned: Optional[float]
    coverage: Optional[float]
    nwords: Optional[int]
    npairs: Optional[int]


class TDEScoreTuple(BaseModel):
    grouping: Optional[CatScores]
    token: Optional[CatScores]
    type: Optional[CatScores]
    boundary: Optional[CatScores]
    matching: Optional[CatScores]
    nlp: Optional[NLPScores]


class EntryDetails(BaseModel):
    train_set: Optional[str]
    benchmarks: List[Benchmark]
    gpu_budget: Optional[str]
    parameters: Dict = Field(default_factory=dict)


class PublicationEntry(BaseModel):
    author_short: Optional[str]
    authors: Optional[str]
    paper_title: Optional[str]
    paper_ref: Optional[str]
    bib_ref: Optional[str]
    paper_url: Optional[Union[AnyHttpUrl, str]]
    pub_year: Optional[int]
    team_name: Optional[str]
    institution: str
    code: Optional[AnyHttpUrl]
    DOI: Optional[str]
    open_science: bool = False


class LeaderboardScores(BaseModel):
    pass


class LeaderboardExtras(BaseModel):
    pass


class LeaderboardEntry(BaseModel):
    model_id: Optional[str]
    submission_id: str = ""
    index: Optional[int]
    submission_date: Optional[datetime]
    submitted_by: Optional[str]
    description: str
    publication: PublicationEntry
    details: EntryDetails
    scores: LeaderboardScores
    extras: Optional[LeaderboardExtras]


class Leaderboard(BaseModel):
    _type: Benchmark
    last_modified: datetime
    data: List[LeaderboardEntry]

    def sort_by(self, key: str):
        """ Sort entries of leaderboard by a specific key"""
        self.data.sort(key=lambda x: getattr(x, key))
