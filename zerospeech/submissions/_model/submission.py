import abc
from functools import wraps
from pathlib import Path
from typing import List, Type, TYPE_CHECKING
from typing import Optional, ClassVar

from pydantic import BaseModel
from pydantic import Field

from zerospeech.generics import Item, Namespace
from zerospeech.out import error_console, warning_console
from zerospeech.tasks import BenchmarkParameters
from .meta_file import MetaFile
from .score_dir import ScoreDir
from .validation_context import ValidationResponse, ValidationWarning

if TYPE_CHECKING:
    from zerospeech.datasets import Dataset


def validation_fn(target: str):
    """ Wrapper function to mark validation items """

    def fn_wrapper(method):
        @wraps(method)
        def _impl(self, *method_args, **method_kwargs):
            return method(self, *method_args, **method_kwargs)

        _impl._validation_fn = True
        _impl._validation_target = target
        return _impl

    return fn_wrapper


def add_item(item_name: str, resp: List[ValidationResponse]):
    """ Add item name to Validation Response list """
    for r in resp:
        r.item_name = item_name


def add_filename(filename: str, resp: List[ValidationResponse]):
    """ Add filename to a Validation Response List """
    for r in resp:
        r.filename = filename


def show_errors(resp: List[ValidationResponse], allow_warnings: bool = True):
    """ Print ValidationResponse Error (and warnings) """
    error_list = [r for r in resp if not r.ok()]

    if not allow_warnings:
        error_list = [r for r in resp if not r.warning()]

    for item in error_list:
        if item.warning() and allow_warnings:
            warning_console.log(item)
        else:
            error_console.log(item)

    # errors only fail the validation
    return len([r for r in resp if not r.valid()]) != 0


class SubmissionValidation(BaseModel, abc.ABC):
    dataset: "Dataset"

    def _is_validation_fn(self, fn_name):
        fn = getattr(self, fn_name, {})
        return getattr(fn, '_validation_fn', False)

    def _get_validation_target(self, fn_name):
        fn = getattr(self, fn_name, {})
        return getattr(fn, '_validation_target')

    def validate(self, submission: 'Submission') -> List[ValidationResponse]:
        validators_items = {
            f"{self._get_validation_target(a)}": getattr(self, a)
            for a in dir(self) if self._is_validation_fn(a)
        }

        results = []
        for name, item in iter(submission.items):
            validator = validators_items.get(name, None)
            if validator is not None:
                res = validator(item)
                results.extend(res)
            else:
                results.append(ValidationWarning("no validation found", item_name=name))

        return results


class Submission(BaseModel, abc.ABC):
    location: Path
    items: Optional[Namespace[Item]]
    params_obj: Optional["BenchmarkParameters"] = None
    meta_obj: Optional[MetaFile] = None
    __score_dir__: Optional[Path] = None
    __score_cls__: ClassVar[Type[ScoreDir]]
    validation_output: List[ValidationResponse] = Field(default_factory=list)

    class Config:
        arbitrary_types_allowed = True

    @property
    def valid(self) -> bool:
        if len(self.validation_output) == 0:
            self.__validate_submission__()

        bad_res = [rs for rs in self.validation_output if not rs.valid()]
        return len(bad_res) == 0

    @property
    def params_file(self):
        return self.location / BenchmarkParameters.file_stem

    @property
    def meta_file(self):
        return self.location / 'meta.yaml'

    @property
    def leaderboard_file(self) -> Path:
        return self.score_dir / "leaderboard.json"

    @property
    def params(self):
        if self.params_obj is None:
            self.params_obj = self.load_parameters()
        return self.params_obj

    @property
    def meta(self):
        if self.meta_obj is None:
            self.meta_obj = MetaFile.from_file(self.meta_file)
        return self.meta_obj

    @property
    def score_dir(self) -> Path:
        """ Get scores location """
        if self.__score_dir__ is None:
            return self.location / 'scores'
        return self.__score_dir__

    @score_dir.setter
    def score_dir(self, score_location: Path):
        """ Set alternative scores location """
        self.__score_dir__ = score_location

    def has_scores(self) -> bool:
        """ Check if score dir is emtpy """
        return len(list(self.score_dir.rglob('*'))) > 0

    def get_scores(self):
        if self.score_dir.is_dir():
            return self.__score_cls__(
                location=self.score_dir,
                submission_dir=self.location,
                meta_file=self.meta,
                params=self.params
            )
        return None

    @classmethod
    @abc.abstractmethod
    def load(cls, path: Path, **kwargs):
        pass

    @classmethod
    @abc.abstractmethod
    def init_dir(cls, location: Path):
        """ Initialise a directory for submission """
        pass

    @abc.abstractmethod
    def load_parameters(self) -> BenchmarkParameters:
        pass

    @abc.abstractmethod
    def __validate_submission__(self):
        pass

    @abc.abstractmethod
    def __zippable__(self):
        pass
