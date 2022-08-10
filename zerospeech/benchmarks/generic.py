import abc

from pydantic import BaseModel, root_validator

from ..datasets import Dataset


class Benchmark(BaseModel, abc.ABC):
    """ A Generic benchmark class """
    dataset: Dataset

    @property
    def name(self) -> str:
        return getattr(self, '_name')

    @root_validator(pre=True)
    def base_validation(cls, values):
        assert hasattr(cls, "_name"), f"A benchmark requires a name (add a _name attribute to the subclass {cls})"

        return values


class BenchmarkTest(Benchmark):
    _name = "zrNamed"
