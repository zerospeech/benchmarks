from collections import namedtuple
from typing import List, Optional

from pydantic import BaseModel

from .abc import LeaderboardEntry, LeaderboardScores, Leaderboard, Benchmark, LeaderboardExtras


class LexicalByLength(BaseModel):
    length: int
    dev_score: float
    dev_std: float
    dev_n: float
    test_score: float
    test_std: float
    test_n: float


class LexicalByFrequency(BaseModel):
    frequency: str
    dev_score: float
    dev_std: float
    dev_n: float
    test_score: float
    test_std: float
    test_n: float


class LexicalExtras(BaseModel):
    by_length: List[LexicalByLength]
    by_frequency: List[LexicalByFrequency]


class SyntacticExtras(BaseModel):
    typeset: str
    dev_score: float
    dev_std: float
    dev_n: float
    test_score: float
    test_std: float
    test_n: float


class SemanticExtras(BaseModel):
    set: str
    dataset: str
    librispeech: float
    synthetic: float


class SLM21Extras(LeaderboardExtras):
    lexical: LexicalExtras
    syntactic: List[SyntacticExtras]
    semantic: List[SemanticExtras]


class ScoreTuple(BaseModel):
    dev: Optional[float]
    test: Optional[float]


class LexicalScores(BaseModel):
    in_vocab: Optional[ScoreTuple]
    all: ScoreTuple


class SemanticScoreSets(BaseModel):
    synthetic: ScoreTuple
    librispeech: ScoreTuple


class SemanticScores(BaseModel):
    normal: SemanticScoreSets
    weighted: SemanticScoreSets


class SLM21Scores(LeaderboardScores):
    lexical: LexicalScores
    syntactic: ScoreTuple
    semantic: SemanticScores


class SLM21Entry(LeaderboardEntry):
    scores: SLM21Scores
    extras: SLM21Extras


class SLM21(Leaderboard):
    data: List[SLM21Entry]
    _type = Benchmark.sLM_21
