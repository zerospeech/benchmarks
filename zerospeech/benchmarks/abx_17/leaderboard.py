from typing import List

from pydantic import BaseModel

from ...model import m_leaderboard


class ABX17Categories(BaseModel):
    t_1s: m_leaderboard.ABXScoreTuple
    t_10s: m_leaderboard.ABXScoreTuple
    t_120s: m_leaderboard.ABXScoreTuple


class ABX17Scores(m_leaderboard.LeaderboardScores):
    english: ABX17Categories
    french: ABX17Categories
    mandarin: ABX17Categories
    german: ABX17Categories
    wolof: ABX17Categories


class ABX17Entry(m_leaderboard.LeaderboardEntry):
    scores: ABX17Scores


class ABX17(m_leaderboard.Leaderboard):
    data: List[ABX17Entry]
    _type = m_leaderboard.Benchmark.ABX_17
