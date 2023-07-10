from typing import List, Dict

from pydantic import BaseModel

from ._models import LeaderboardScores, LeaderboardEntry, Leaderboard
from ._types import LeaderboardBenchmarkName


class ProsAuditScoreEntity(BaseModel):
    score: float
    n: int
    std: float


class ProsAuditEntryScores(LeaderboardScores):
    protosyntax: Dict[str, ProsAuditScoreEntity]
    lexical: Dict[str, ProsAuditScoreEntity]


class ProsAuditLeaderboardEntry(LeaderboardEntry):
    scores: ProsAuditEntryScores


class ProsAuditLeaderboard(Leaderboard):
    _type = LeaderboardBenchmarkName.prosAudit
    data: List[ProsAuditLeaderboardEntry]
