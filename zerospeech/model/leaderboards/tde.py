from typing import List, Optional

from pydantic import BaseModel

from .abc import LeaderboardEntry, LeaderboardScores, Leaderboard, Benchmark


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


# TDE-15 ------------------------
class TDE15Scores(LeaderboardScores):
    english: TDEScoreTuple
    xitsonga: TDEScoreTuple


class TDE15Entry(LeaderboardEntry):
    scores: TDE15Scores


class TDE15(Leaderboard):
    data: List[TDE15Entry]
    _type = Benchmark.TDE_15


# TDE-17 ------------------------
class TDE17Scores(LeaderboardScores):
    english: TDEScoreTuple
    french: TDEScoreTuple
    mandarin: TDEScoreTuple
    german: TDEScoreTuple
    wolof: TDEScoreTuple


class TDE17Entry(LeaderboardEntry):
    scores: TDE17Scores


class TDE17(Leaderboard):
    data: List[TDE17Entry]
    _type = Benchmark.TDE_17
