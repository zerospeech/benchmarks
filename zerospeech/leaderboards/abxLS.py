from typing import List, Literal, Optional, Union

from pydantic import BaseModel, validator

from ._types import LeaderboardBenchmarkName
from ._models import LeaderboardScores, LeaderboardEntry, Leaderboard


class ABXLSScoreSubType(BaseModel):
    subset: Literal['dev-clean', 'dev-other', 'test-clean', 'test-other']
    granularity: Literal['triphone', 'phoneme']
    speaker_mode: Literal['across', 'within']
    context_mode: Literal['within', 'any']
    score: float
    pooling: str
    seed: Optional[int]

    @validator('seed', pre=True)
    def seed_int(cls, v):
        """ Fix seed none-type formatting issues"""
        try:
            return int(v)
        except ValueError:
            return None


class ABXLSScoreSubSet(BaseModel):
    dev: ABXLSScoreSubType
    test: ABXLSScoreSubType


class ABXLSScoresSubSubType(BaseModel):
    within: ABXLSScoreSubSet
    across: ABXLSScoreSubSet


class ABXLSScoreType(BaseModel):
    clean: ABXLSScoresSubSubType
    other: ABXLSScoresSubSubType


class ABXLSScoreClass(BaseModel):
    any: Optional[ABXLSScoreType]
    within: Optional[ABXLSScoreType]


class ABXLSScore(LeaderboardScores):
    phoneme: ABXLSScoreClass
    triphone: ABXLSScoreClass


class ABXLSEntry(LeaderboardEntry):
    scores: ABXLSScore


class ABXLSLeaderboard(Leaderboard):
    data: List[ABXLSEntry]
    _type = LeaderboardBenchmarkName.ABX_LS
