import enum

from ..model import m_benchmark, m_score_dir
from ._benchmarks import sLM_21, abx_LS, tde_17


class BenchmarkList(str, enum.Enum):
    """ Simplified enum """

    def __new__(
            cls,
            label, benchmark, submission: m_benchmark.Submission,
            score_dir: m_score_dir.ScoreDir
    ):
        """ Allow setting parameters on enum """
        obj = str.__new__(cls, label)
        obj._value_ = label
        obj.benchmark = benchmark
        obj.submission = submission
        obj.score_dir = score_dir
        return obj

    sLM21 = 'sLM21', sLM_21.SLM21Benchmark, sLM_21.SLM21Submission, sLM_21.SLM21ScoreDir
    abx_LS = 'abxLS', abx_LS.AbxLSBenchmark, abx_LS.AbxLSSubmission, abx_LS.ABXLSScoreDir
    tde_17 = 'tde17', tde_17.TDE17Benchmark, tde_17.TDE17Submission, None
