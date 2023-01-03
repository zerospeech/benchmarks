import abc
from functools import wraps
from pathlib import Path
from typing import List, Any, Type, Dict
from typing import Optional, ClassVar

from pydantic import BaseModel
from pydantic import root_validator, Field

from .data_items import Item
from .datasets import Dataset
from .datasets import Namespace
from .meta_file import MetaFile
from .score_dir import ScoreDir
from ..out import console as out_console, void_console, error_console, warning_console


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


class ValidationResponse(abc.ABC):
    """ Abstract class defining a Message object specifying validation Errors/Warnings/Checks """

    def __init__(self, msg, *, data=None, item_name=None, filename=None, location=None):
        self.item_name = item_name
        self.filename = filename
        self.location = location
        self.msg = msg
        self.data = data

    def valid(self):
        return getattr(self, '__is_valid__', False)

    def warning(self):
        return getattr(self, '__is_warning__', False)

    def error(self):
        return getattr(self, '__is_error__', False)

    def ok(self):
        return getattr(self, '__is_ok__', False)

    def __str__(self):
        item_name = '-'
        if self.item_name:
            item_name = self.item_name
        filename = '[-'
        if self.filename:
            filename = f"[{self.filename}"
        location = ':-]'
        if self.location:
            location = f":{self.location}]"
        msg = ''
        if self.msg:
            msg = self.msg

        cls_name = self.__class__.__name__
        return f'{cls_name}({item_name}){filename}{location}>> {msg}'


class ValidationWarning(ValidationResponse):
    """ Class designating a validation warning """
    __is_warning__ = True
    __is_valid__ = True


class ValidationError(ValidationResponse):
    """ Class designating a validation error """
    __is_error__ = True
    __is_valid__ = False


class ValidationOK(ValidationResponse):
    """ Class designating a successful validation check """
    __is_ok__ = True
    __is_valid__ = True


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
    # todo: add validation of Metafile as well
    dataset: Dataset

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


class InvalidSubmissionError(Exception):
    """ Error used to signal a non valid submission """
    pass


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


class Submission(BaseModel, abc.ABC):
    location: Path
    items: Optional[Namespace[Item]]
    params_obj: BenchmarkParameters = None
    meta_obj: Optional[MetaFile] = None
    validation_output: List[ValidationResponse] = Field(default_factory=list)
    __score_dir__: Optional[Path] = None
    __score_cls__: ClassVar[Type[ScoreDir]]

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
    def leaderboard_file(self):
        return self.location / 'leaderboard.json'

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

    @property
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
    def eval(self, submission: Submission, dataset: Dataset):
        """ Evaluation method """
        pass


class Benchmark(BaseModel, abc.ABC):
    """ A Generic benchmark class """
    dataset: Dataset
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
    def run(self, submission: Submission):
        """ Run the benchmark """
        pass
