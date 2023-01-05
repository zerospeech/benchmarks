from typing import List, Literal

from zerospeech.model import m_leaderboard


class ABXLSScore(m_leaderboard.LeaderboardScores):
    subset: Literal['dev-clean', 'dev-other', 'test-clean', 'test-other']
    granularity: Literal['triphone', 'phoneme']
    speaker_mode: Literal['across', 'within']
    context_mode: Literal['within', 'any']
    score: float
    pooling: str
    seed: int


class ABXLSEntry(m_leaderboard.LeaderboardEntry):
    scores: List[ABXLSScore]


class ABXLS(m_leaderboard.Leaderboard):
    data: List[ABXLSEntry]
    _type = m_leaderboard.Benchmark.ABX_LS
