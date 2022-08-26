from typing import List, Optional, Tuple

from pydantic import BaseModel

from .abc import LeaderboardEntry, LeaderboardScores, Leaderboard, Benchmark, LeaderboardExtras


class DetailedABXTuples(BaseModel):
    auxiliary1_abx_dtw_cosine: Optional[float]
    auxiliary1_abx_dtw_kl: Optional[float]
    auxiliary1_abx_levenshtein: Optional[float]
    auxiliary2_abx_dtw_cosine: Optional[float]
    auxiliary2_abx_dtw_kl: Optional[float]
    auxiliary2_abx_levenshtein: Optional[float]
    test_abx_dtw_cosine: Optional[float]
    test_abx_dtw_kl: Optional[float]
    test_abx_levenshtein: Optional[float]


class DetailedABX(BaseModel):
    english: DetailedABXTuples
    austronesian: DetailedABXTuples


class DetailedBitrateTuples(BaseModel):
    auxiliary1_bitrate: Optional[float]
    auxiliary2_bitrate: Optional[float]
    test_bitrate: Optional[float]


class DetailedBitrate(BaseModel):
    english: DetailedBitrateTuples
    austronesian: DetailedBitrateTuples


class TTSO19DetailedScores(BaseModel):
    abx: DetailedABX
    bitrate: DetailedBitrate


class TTSOAudioSampleEntry(BaseModel):
    sample_1: Optional[str]
    sample_2: Optional[str]


class TTSOAudioSamples(BaseModel):
    english: TTSOAudioSampleEntry
    austronesian: TTSOAudioSampleEntry


class TTS019Extras(LeaderboardExtras):
    audio_samples: TTSOAudioSamples
    detailed_scores: TTSO19DetailedScores
    extra_description: Tuple


class TTS019ScoresTuple(BaseModel):
    mos: Optional[float]
    cer: Optional[float]
    similarity: Optional[float]
    abx: Optional[float]
    bitrate: Optional[float]


class TTS019Scores(LeaderboardScores):
    english: TTS019ScoresTuple
    austronesian: TTS019ScoresTuple


class TTS019Entry(LeaderboardEntry):
    scores: TTS019Scores
    extras: TTS019Extras


class TTS019(Leaderboard):
    data: List[TTS019Entry]
    _type = Benchmark.TTS0_19
