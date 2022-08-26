from typing import List

from ...model import m_leaderboard


class TDE15Scores(m_leaderboard.LeaderboardScores):
    english: m_leaderboard.TDEScoreTuple
    xitsonga: m_leaderboard.TDEScoreTuple


class TDE15Entry(m_leaderboard.LeaderboardEntry):
    scores: TDE15Scores


class TDE15(m_leaderboard.Leaderboard):
    data: List[TDE15Entry]
    _type = m_leaderboard.Benchmark.TDE_15
   