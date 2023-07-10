from typing import List, Optional

from pydantic import BaseModel, Field

from ._models import LeaderboardScores, LeaderboardEntry, LeaderboardExtras, Leaderboard
from ._types import LeaderboardBenchmarkName


class LexicalByLength(BaseModel):
    length: int
    dev_score: float = Field(alias="score_dev")
    dev_std: float = Field(alias="std_dev")
    dev_n: float = Field(alias="n_dev")
    test_score: float = Field(alias="score_test")
    test_std: float = Field(alias="std_test")
    test_n: float = Field(alias="n_test")

    class Config:
        allow_population_by_field_name = True


class LexicalByFrequency(BaseModel):
    frequency: str
    dev_score: float = Field(alias="score_dev")
    dev_std: float = Field(alias="std_dev")
    dev_n: float = Field(alias="n_dev")
    test_score: float = Field(alias="score_test")
    test_std: float = Field(alias="std_test")
    test_n: float = Field(alias="n_test")

    class Config:
        allow_population_by_field_name = True


class LexicalExtras(BaseModel):
    by_length: List[LexicalByLength]
    by_frequency: List[LexicalByFrequency]


class SyntacticExtras(BaseModel):
    typeset: str
    dev_score: float = Field(alias="score_dev")
    dev_std: float = Field(alias="std_dev")
    dev_n: float = Field(alias="n_dev")
    test_score: float = Field(alias="score_test")
    test_std: float = Field(alias="std_test")
    test_n: float = Field(alias="n_test")

    class Config:
        allow_population_by_field_name = True


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


class SLM21LeaderboardEntry(LeaderboardEntry):
    scores: SLM21Scores
    extras: SLM21Extras


class SLM21Leaderboard(Leaderboard):
    data: List[SLM21LeaderboardEntry]
    _type = LeaderboardBenchmarkName.sLM_21
