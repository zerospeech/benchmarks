from typing import List, Optional

from pydantic import BaseModel

from .abc import LeaderboardEntry, LeaderboardScores, Leaderboard, Benchmark


class ABXScoreTuple(BaseModel):
    within: Optional[float]
    across: Optional[float]


# ABX-15 ------------------------
class ABX15Scores(LeaderboardScores):
    english: ABXScoreTuple
    xitsonga: ABXScoreTuple


class ABX15Entry(LeaderboardEntry):
    scores: ABX15Scores


class ABX15(Leaderboard):
    data: List[ABX15Entry]
    _type = Benchmark.ABX_15


# ABX-17 ------------------------
class ABX17Categories(BaseModel):
    t_1s: ABXScoreTuple
    t_10s: ABXScoreTuple
    t_120s: ABXScoreTuple


class ABX17Scores(LeaderboardScores):
    english: ABX17Categories
    french: ABX17Categories
    mandarin: ABX17Categories
    german: ABX17Categories
    wolof: ABX17Categories


class ABX17Entry(LeaderboardEntry):
    scores: ABX17Scores


class ABX17(Leaderboard):
    data: List[ABX17Entry]
    _type = Benchmark.ABX_17


# ABX-LS ------------------------

class ABXLSScoresSet(BaseModel):
    dev: ABXScoreTuple
    test: ABXScoreTuple


class ABXLSScores(LeaderboardScores):
    clean: ABXLSScoresSet
    other: ABXLSScoresSet


class ABXLSEntry(LeaderboardEntry):
    scores: ABXLSScores


class ABXLS(Leaderboard):
    data: List[ABXLSEntry]
    _type = Benchmark.ABX_LS

