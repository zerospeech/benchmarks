import abc
from pathlib import Path
from typing import TYPE_CHECKING, ClassVar, Type

from pydantic import BaseModel
from pydantic import root_validator

from zerospeech.out import console as out_console, void_console

if TYPE_CHECKING:
    from zerospeech.submissions import Submission
    from zerospeech.datasets import Dataset


class NoSubmissionTypeError(Exception):
    """ This benchmark has not specified submission type"""
    pass


class Benchmark(BaseModel, abc.ABC):
    """ A Generic benchmark class """
    _name: ClassVar[str] = ...
    _doc_url: ClassVar[str] = ...
    __submission_cls__: Type["Submission"] = ...
    dataset: "Dataset"
    quiet: bool = False

    @classmethod
    def docs(cls):
        text = getattr(cls, "__doc__", 'No information provided')
        url = getattr(cls, '_doc_url', None)
        if url:
            text += f"For more information visit: {url}"
        return text

    @property
    def name(self) -> str:
        return getattr(self, '_name')

    @property
    def doc_url(self) -> str:
        return getattr(self, '_doc_url')

    @property
    def console(self):
        if self.quiet:
            return void_console
        return out_console

    @root_validator(pre=True)
    def base_validation(cls, values):
        assert hasattr(cls, "_name"), f"A benchmark requires a name (add a _name attribute to the subclass {cls})"
        assert hasattr(cls, "_doc_url"), f"A benchmark requires a name (add a _doc_url attribute to the subclass {cls})"
        return values

    def load_submission(self, location: Path, **kwargs) -> "Submission":
        """ Load a submission using specified submission type """
        if hasattr(self, '__submission_cls__'):
            return self.__submission_cls__.load(location, **kwargs)
        raise NoSubmissionTypeError(f'No submission type in benchmark  {self._name}')

    def init_submission_dir(self, location: Path):
        if hasattr(self, '__submission_cls__'):
            return self.__submission_cls__.init_dir(location)
        raise NoSubmissionTypeError(f'No submission type in benchmark {self._name}')

    @abc.abstractmethod
    def run(self, submission: "Submission"):
        """ Run the benchmark """
        pass
