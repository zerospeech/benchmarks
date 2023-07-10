import abc
from pathlib import Path
from typing import ClassVar, Dict, Any
from typing import TYPE_CHECKING

from pydantic import BaseModel
from pydantic import root_validator

from zerospeech.out import console as out_console, void_console

if TYPE_CHECKING:
    from zerospeech.submissions import Submission
    from zerospeech.datasets import Dataset


class BenchmarkParameters(BaseModel, abc.ABC):
    """ Abstract Parameter class """
    file_stem: ClassVar[str] = "params.yaml"
    quiet: bool = False

    @abc.abstractmethod
    def to_meta(self) -> Dict[str, Any]:
        """ Convert into leaderboard meta entry """
        pass

    @abc.abstractmethod
    def export(self, file: Path):
        """ Export to file """
        pass


class Task(BaseModel, abc.ABC):
    """ Abstract definition of a task """
    quiet: bool = False

    @property
    def name(self) -> str:
        return getattr(self, '_name')

    @property
    def console(self):
        """ Console to print output """
        if self.quiet:
            return void_console
        return out_console

    @root_validator(pre=True)
    def base_validation(cls, values):
        assert hasattr(cls, "_name"), f"A benchmark requires a name (add a _name attribute to the subclass {cls})"

        return values

    @abc.abstractmethod
    def eval(self, submission: "Submission", dataset: "Dataset"):
        """ Evaluation method """
        pass
