import enum
from pathlib import Path

import yaml

from ..model import m_benchmark, m_meta_file
from ._benchmarks import sLM_21, abx_LS, tde_17, abx_17, pros_audit


class InvalidBenchmarkError(Exception):
    pass


class BenchmarkList(str, enum.Enum):
    """ Simplified enum """

    def __new__(
            cls,
            benchmark: m_benchmark.Benchmark, submission: m_benchmark.Submission
    ):
        """ Allow setting parameters on enum """
        label = benchmark._name # noqa: allow private access
        obj = str.__new__(cls, label)
        obj._value_ = label
        obj.benchmark = benchmark
        obj.submission = submission
        obj.doc_url = benchmark._doc_url  # noqa: allow private access
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

