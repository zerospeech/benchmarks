from collections import defaultdict
from typing import Dict, Tuple

from pydantic import root_validator

try:
    from tts019_evaluation import bitrate, abx, audio
except ImportError:
    bitrate = None
    abx = None
    audio = None

from zerospeech.model import m_benchmark


class TTS019BitrateEval(m_benchmark.Task):
    _name = "tts0-bitrate"
    tasks: Tuple[str, ...] = ('test', 'auxiliary_embedding1', 'auxiliary_embedding2')
    languages: Tuple[str, ...] = ('english', 'indonesian')
    distance_units: Tuple[str, ...] = ('cosine', 'KL', 'levenshtein')

    @root_validator(pre=True)
    def check_order_id(cls, values):
        if bitrate is None:
            raise ImportError(f'Module: zerospeech-tts019 is not installed cannot run {cls.__name__}')
        return values

    def eval(self, submission: m_benchmark.Submission, dataset: m_benchmark.Dataset) -> Dict:
        """ Evaluation of bitrate """
        results = defaultdict(dict)

        for lang in self.languages:
            for task in self.tasks:
                """
                TODO: Fix arguments to correspond to calculation
                1) Get features file list (should be in dataset ??)  
                2) features files should be in submission
                2) see if log or raise can be modified ?
                """
                results[lang][task] = bitrate.calculate_bitrate(..., ..., log=True)

        return results


class TTS019ABXEval(m_benchmark.Task):
    _name = "tts0-abx"
    tasks: Tuple[str, ...] = ('test', 'auxiliary_embedding1', 'auxiliary_embedding2')
    languages: Tuple[str, ...] = ('english', 'indonesian')
    distance_units: Tuple[str, ...] = ('cosine', 'KL', 'levenshtein')

    @root_validator(pre=True)
    def check_order_id(cls, values):
        if abx is None:
            raise ImportError(f'Module: zerospeech-tts019 is not installed cannot run {cls.__name__}')
        return values

    def eval(self, submission: m_benchmark.Submission, dataset: m_benchmark.Dataset) -> Dict:
        """ Evaluation of bitrate """
        return dict()


class TTS019AudioEval(m_benchmark.Task):
    _name = "tts0-audio"
    tasks: Tuple[str, ...] = ('test', 'auxiliary_embedding1', 'auxiliary_embedding2')
    languages: Tuple[str, ...] = ('english', 'indonesian')
    distance_units: Tuple[str, ...] = ('cosine', 'KL', 'levenshtein')

    @root_validator(pre=True)
    def check_order_id(cls, values):
        if audio is None:
            raise ImportError(f'Module: zerospeech-tts019 is not installed cannot run {cls.__name__}')
        return values

    def eval(self, submission: m_benchmark.Submission, dataset: m_benchmark.Dataset) -> Dict:
        """ Evaluation of bitrate """
        return dict()
