import enum
from pathlib import Path
from typing import Type

import yaml

from ..model import m_benchmark, m_meta_file
from ._benchmarks import sLM_21, abx_LS, tde_17, abx_17, pros_audit


class InvalidBenchmarkError(Exception):
    pass


class BenchmarkList(str, enum.Enum):
    """ Simplified enum """

    def __new__(
            cls,
            benchmark: Type[m_benchmark.Benchmark], submission: Type[m_benchmark.Submission]
    ):
        """ Allow setting parameters on enum """
        label = benchmark._name  # noqa: allow private access
        obj = str.__new__(cls, label)
        obj._value_ = label
        obj._benchmark = benchmark
        obj._submission = submission
        obj._doc_url = benchmark._doc_url  # noqa: allow private access
        return obj

    sLM21 = sLM_21.SLM21Benchmark, sLM_21.SLM21Submission
    abx_LS = abx_LS.AbxLSBenchmark, abx_LS.AbxLSSubmission
    # TODO: implement score_dir, leaderboard & verification
    abx_17 = abx_17.ABX17Benchmark, abx_17.ABX17Submission
    # TODO: implement score_dir, leaderboard & verification
    tde_17 = tde_17.TDE17Benchmark, tde_17.TDE17Submission
    pros_audit = pros_audit.SLMProsodyBenchmark, pros_audit.ProsodySubmission

    @classmethod
    def from_submission(cls, location: Path) -> "BenchmarkList":
        benchmark_name = m_meta_file.MetaFile.benchmark_from_submission(location)
        if benchmark_name is None:
            raise m_benchmark.InvalidSubmissionError("meta.yaml not found or invalid")

        try:
            return cls(benchmark_name)
        except ValueError:
            raise InvalidBenchmarkError(f"{benchmark_name} is not a valid benchmark !!")

    @property
    def benchmark(self) -> Type[m_benchmark.Benchmark]:
        """ Benchmark Class (used for typing mostly) """
        return self._benchmark

    @property
    def submission(self) -> Type[m_benchmark.Submission]:
        """ Submission Class property (used for typing mostly) """
        return self._submission

    @property
    def doc_url(self) -> str:
        return self._doc_url

    @property
    def name(self) -> str:
        return self._value_
