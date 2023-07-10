import enum
from datetime import date
from pathlib import Path
from typing import Type, Optional, TYPE_CHECKING

from pydantic import BaseModel

from misc import InvalidSubmissionError
from zerospeech.benchmarks import sLM21, abxLS, tde17, abx17, prosAudit
from zerospeech.httpw import get as http_get, APIHTTPException
from zerospeech.settings import get_settings
from zerospeech.submissions import MetaFile
from ._model import Benchmark

if TYPE_CHECKING:
    from zerospeech.submissions import Submission

st = get_settings()


class InvalidBenchmarkError(Exception):
    pass


class _InfoSchema(BaseModel):
    label: str
    start_date: date
    end_date: Optional[date]
    active: bool
    url: str
    evaluator: Optional[int]
    auto_eval: bool

    @property
    def is_open(self):
        """ Check if benchmark is open to submissions """
        if self.end_date is not None:
            return self.active and self.end_date >= date.today()
        return self.active


class BenchmarkList(str, enum.Enum):
    """ Simplified enum """

    def __new__(
            cls,
            benchmark: Type[Benchmark], submission: Type["Submission"]
    ):
        """ Allow setting parameters on enum """
        label = benchmark._name  # noqa: allow private access
        obj = str.__new__(cls, label)
        obj._value_ = label
        obj._benchmark = benchmark
        obj._submission = submission
        obj._doc_url = benchmark._doc_url  # noqa: allow private access
        obj.is_test = False
        return obj

    sLM21 = sLM21.SLM21Benchmark, sLM21.SLM21Submission
    abx_LS = abxLS.AbxLSBenchmark, abxLS.AbxLSSubmission
    pros_audit = prosAudit.SLMProsodyBenchmark, prosAudit.ProsodySubmission
    # TODO: implement score_dir, leaderboard & validation for 2017 (tde & abx)
    abx_17 = abx17.ABX17Benchmark, abx17.ABX17Submission
    tde_17 = tde17.TDE17Benchmark, tde17.TDE17Submission


    @classmethod
    def from_submission(cls, location: Path) -> "BenchmarkList":
        benchmark_name = MetaFile.benchmark_from_submission(location)
        if benchmark_name is None:
            raise InvalidSubmissionError("meta.yaml not found or invalid")

        try:
            if benchmark_name.startswith("test-"):
                benchmark_name = benchmark_name.replace("test-", "")
                bench = cls(benchmark_name)
                bench.is_test = True
            else:
                bench = cls(benchmark_name)
            return bench
        except ValueError:
            raise InvalidBenchmarkError(f"{benchmark_name} is not a valid benchmark !!")

    @property
    def benchmark(self) -> Type[Benchmark]:
        """ Benchmark Class (used for typing mostly) """
        return self._benchmark

    @property
    def submission(self) -> Type["Submission"]:
        """ Submission Class property (used for typing mostly) """
        return self._submission

    @property
    def doc_url(self) -> str:
        return self._doc_url

    @property
    def name(self) -> str:
        return self._value_

    def info(self) -> _InfoSchema:
        """ Get benchmark information from back-end"""
        benchmark_id = self.value
        if self.is_test:
            benchmark_id = "test-challenge"

        route, _ = st.api.request_params('benchmark_info', benchmark_id=benchmark_id)
        response = http_get(route)
        if response.status_code != 200:
            raise APIHTTPException.from_request('benchmark_info', response)
        return _InfoSchema.parse_obj(response.json())

    def is_active(self) -> bool:
        """ Check if benchmark accepts new submissions """
        return self.info().is_open
