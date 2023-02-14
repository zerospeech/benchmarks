from typing import List

from pydantic import BaseModel

from zerospeech.model import m_leaderboard


class ProsAuditScoreEntity(BaseModel):
    score: float
    n: int
    std: float


class ProsAuditScores(m_leaderboard.LeaderboardScores):
    protosyntax: ProsAuditScoreEntity
    lexical: ProsAuditScoreEntity


class ProsAuditLeaderboardEntry(m_leaderboard.LeaderboardEntry):
    scores = ProsAuditScores


class ProsAuditLeaderboard(m_leaderboard.Leaderboard):
    data = List[ProsAuditLeaderboardEntry]
    _type = m_leaderboard.Benchmark.prosAudit
