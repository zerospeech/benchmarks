from typing import List

from pydantic import BaseModel

from ....model import m_leaderboard


class ABXLSScoresSet(BaseModel):
    dev: m_leaderboard.ABXScoreTuple
    test: m_leaderboard.ABXScoreTuple


class ABXLSScores(m_leaderboard.LeaderboardScores):
    clean: ABXLSScoresSet
    other: ABXLSScoresSet


class ABXLSEntry(m_leaderboard.LeaderboardEntry):
    scores: ABXLSScores


class ABXLS(m_leaderboard.Leaderboard):
    data: List[ABXLSEntry]
    _type = m_leaderboard.Benchmark.ABX_LS
