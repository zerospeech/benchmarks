from typing import List

from ._models import LeaderboardScores, LeaderboardEntry, Leaderboard, TDEScoreTuple
from ._types import LeaderboardBenchmarkName


class TDE17Scores(LeaderboardScores):
    english: TDEScoreTuple
    french: TDEScoreTuple
    mandarin: TDEScoreTuple
    german: TDEScoreTuple
    wolof: TDEScoreTuple


class TDE17Entry(LeaderboardEntry):
    scores: TDE17Scores


class TDE17Leaderboard(Leaderboard):
    data: List[TDE17Entry]
    _type = LeaderboardBenchmarkName.TDE_17
