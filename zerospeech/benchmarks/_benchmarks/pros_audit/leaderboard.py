from typing import List, Dict

from pydantic import BaseModel

from zerospeech.model import m_leaderboard


class ProsAuditScoreEntity(BaseModel):
    score: float
    n: int
    std: float


class ProsAuditEntryScores(m_leaderboard.LeaderboardScores):
    protosyntax: Dict[str, ProsAuditScoreEntity]
    lexical: Dict[str, ProsAuditScoreEntity]


class ProsAuditLeaderboardEntry(m_leaderboard.LeaderboardEntry):
    scores: ProsAuditEntryScores


class ProsAuditLeaderboard(m_leaderboard.Leaderboard):
    data: List[ProsAuditLeaderboardEntry]
    _type = m_leaderboard.Benchmark.prosAudit
