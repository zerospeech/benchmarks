from typing import List

from ...model import m_leaderboard


class ABX15Scores(m_leaderboard.LeaderboardScores):
    english: m_leaderboard.ABXScoreTuple
    xitsonga: m_leaderboard.ABXScoreTuple


class ABX15Entry(m_leaderboard.LeaderboardEntry):
    scores: ABX15Scores


class ABX15(m_leaderboard.Leaderboard):
    data: List[ABX15Entry]
    _type = m_leaderboard.Benchmark.ABX_15

