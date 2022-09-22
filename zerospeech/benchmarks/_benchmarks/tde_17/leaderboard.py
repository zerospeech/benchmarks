from typing import List

from ....model import m_leaderboard


class TDE17Scores(m_leaderboard.LeaderboardScores):
    english: m_leaderboard.TDEScoreTuple
    french: m_leaderboard.TDEScoreTuple
    mandarin: m_leaderboard.TDEScoreTuple
    german: m_leaderboard.TDEScoreTuple
    wolof: m_leaderboard.TDEScoreTuple


class TDE17Entry(m_leaderboard.LeaderboardEntry):
    scores: TDE17Scores


class TDE17(m_leaderboard.Leaderboard):
    data: List[TDE17Entry]
    _type = m_leaderboard.Benchmark.TDE_17
