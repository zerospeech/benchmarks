import enum

from . import sLM_21


class BenchmarkList(str, enum.Enum):
    """ Simplified enum """

    def __new__(cls, label, benchmark, submission, parameters):
        """ Allow setting parameters on enum """
        obj = str.__new__(cls, label)
        obj._value_ = label
        obj.benchmark = benchmark
        obj.submission = submission
        obj.parameters = parameters
        return obj

    sLM21 = 'sLM21', sLM_21.SLM21Benchmark, sLM_21.SLM21Submission, sLM_21.SLM21BenchmarkParameters
