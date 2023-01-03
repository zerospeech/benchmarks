import enum

from ..model import m_benchmark, m_score_dir
from ._benchmarks import sLM_21, abx_LS, tde_17, abx_17


class BenchmarkList(str, enum.Enum):
    """ Simplified enum """

    def __new__(
            cls,
            benchmark, submission: m_benchmark.Submission,
            score_dir: m_score_dir.ScoreDir
    ):
        """ Allow setting parameters on enum """
        label = benchmark._name # noqa: allow private access
        obj = str.__new__(cls, label)
        obj._value_ = label
        obj.benchmark = benchmark
        obj.submission = submission
        obj.score_dir = score_dir
        obj.doc_url = benchmark._doc_url  # noqa: allow private access
        return obj

    sLM21 = sLM_21.SLM21Benchmark, sLM_21.SLM21Submission, sLM_21.SLM21ScoreDir
    abx_LS = abx_LS.AbxLSBenchmark, abx_LS.AbxLSSubmission, abx_LS.ABXLSScoreDir
    # TODO: implement score_dir, leaderboard & verification
    abx_17 = abx_17.ABX17Benchmark, abx_17.ABX17Submission, None
    # TODO: implement score_dir, leaderboard & verification
    tde_17 = tde_17.TDE17Benchmark, tde_17.TDE17Submission, None

