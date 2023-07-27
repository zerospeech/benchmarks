from typing import List, Literal, Optional

from pydantic import BaseModel, validator

from ._models import LeaderboardScores, LeaderboardEntry, Leaderboard
from ._types import LeaderboardBenchmarkName


class ABXScore(BaseModel):
    within: float
    across: float


class ABX17ScoreLang(BaseModel):
    t_1s: ABXScore
    t_10s: ABXScore
    t_120s: ABXScore


class ABX17LeaderboardScores(LeaderboardScores):
    english: ABX17ScoreLang
    french: ABX17ScoreLang
    mandarin: ABX17ScoreLang
    german: ABX17ScoreLang
    wolof: ABX17ScoreLang


class ABX17LeaderboardEntry(LeaderboardEntry):
    scores: ABX17LeaderboardScores


class ABX17Leaderboard(Leaderboard):
    data: List[ABX17LeaderboardEntry]
    _type = LeaderboardBenchmarkName.ABX_17
