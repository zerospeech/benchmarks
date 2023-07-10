import abc
from typing import TYPE_CHECKING

from pydantic import BaseModel
from pydantic import root_validator

from zerospeech.out import console as out_console, void_console

if TYPE_CHECKING:
    from zerospeech.submissions import Submission
    from zerospeech.datasets import Dataset


class Benchmark(BaseModel, abc.ABC):
    """ A Generic benchmark class """
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

    @abc.abstractmethod
    def run(self, submission: "Submission"):
        """ Run the benchmark """
        pass
