import json
import os
import shutil
import sys
from pathlib import Path
from typing import Tuple, Dict, Any, Optional, Type, List

import yaml
from pydantic import Field

from zerospeech.generics import FileItem, Item, Namespace
from zerospeech.misc import load_obj
from zerospeech.tasks import BenchmarkParameters, tde
from zerospeech.datasets.zrc_2017 import ZRC2017Dataset
from zerospeech.validators import BASE_VALIDATOR_FN_TYPE
from ._model import (
    MetaFile, Submission, validation_fn, SubmissionValidation,
    ValidationResponse, ValidationError, ValidationOK
)


class TDE17BenchmarkParams(BenchmarkParameters):
    """ Parameters for the TDE-17 benchmark """
    # location to output the results
    out: Optional[str] = None
    result_filename: str = "scores.json"

    def get_task(self):
        return self.dict()

    def to_meta(self) -> Dict[str, Any]:
        """ Convert into leaderboard meta entry """
        excluded = {'result_filename', 'out'}
        return dict(self._iter(to_dict=True, exclude=excluded))

    def export(self, file: Path):
        # filtering non-interfaced param values
        excluded = {'result_filename', 'out'}

        # conversion order  self -> json -> pydict -> yaml
        # json is added in before pydict to leverage the pydantic serializer for
        # more complex types as Enum, datetime, etc. as a simpler chain of
        # self -> pydict -> yaml leaves those unserialised and the yaml serializer fails.
        # see https://pydantic-docs.helpmanual.io/usage/types/#standard-library-types
        as_obj = json.loads(self.json(exclude=excluded))
        with file.open('w') as fp:
            yaml.dump(as_obj, fp)


def tde_class_file_check(
        file_location: Path, additional_checks: Optional[List[BASE_VALIDATOR_FN_TYPE]] = None
) -> List[ValidationResponse]:
    """ Check a TDE class file """
    if not file_location.is_file():
        return [ValidationError(
            'Given TDE Disc file does not exist !!!', data=file_location.name, location=file_location.parent
        )]

    # Disc class prints a bunch of nonsense, so we force it to be quiet
    sys.stdout = open(os.devnull, 'w')
    try:
        disc = tde.Disc(str(file_location))
    except Exception as e:  # noqa: broad exception on purpose
        return [ValidationError(f'{e}', data=file_location)]
    finally:
        sys.stdout = sys.__stdout__

    results = [ValidationOK('File is a Disc TDE file !', data=file_location)]

    if additional_checks:
        for fn in additional_checks:
            results.extend(fn(disc))

    return results


class TDE17SubmissionValidation(SubmissionValidation):
    dataset: ZRC2017Dataset = Field(default_factory=lambda: ZRC2017Dataset.load())

    @property
    def params_class(self) -> Type[TDE17BenchmarkParams]:
        return TDE17BenchmarkParams

    @validation_fn(target='english')
    def validating_english(self, class_file: FileItem):
        return tde_class_file_check(class_file.file)

    @validation_fn(target='french')
    def validating_english(self, class_file: FileItem):
        return tde_class_file_check(class_file.file)

    @validation_fn(target='mandarin')
    def validating_english(self, class_file: FileItem):
        return tde_class_file_check(class_file.file)

    @validation_fn(target='german')
    def validating_english(self, class_file: FileItem):
        return tde_class_file_check(class_file.file)

    @validation_fn(target='wolof')
    def validating_english(self, class_file: FileItem):
        return tde_class_file_check(class_file.file)


class TDE17Submission(Submission):
    """ Submission for TDE-17 """
    sets: Tuple = ('1s', '10s', '120s')
    tasks: Tuple = ('english', 'french', 'mandarin', 'german', 'wolof')

    @classmethod
    def load(
            cls, path: Path, *,
            tasks=('english', 'french', 'mandarin', 'german', 'wolof'),
            sets=('1s', '10s', '120s')
    ):
        items = dict()

        if 'english' in tasks:
            items['english'] = FileItem.from_file(
                path / 'english.txt'
            )

        if 'french' in tasks:
            items['french'] = FileItem.from_file(
                path / 'french.txt'
            )

        if 'mandarin' in tasks:
            items['mandarin'] = FileItem.from_file(
                path / 'mandarin.txt'
            )

        if 'german' in tasks:
            items['german'] = FileItem.from_file(
                path / 'german.txt'
            )

        if 'wolof' in tasks:
            items['wolof'] = FileItem.from_file(
                path / 'wolof.txt'
            )

        submission = cls(
            sets=sets,
            tasks=tasks,
            location=path,
            items=Namespace[Item](store=items)
        )
        # if params not set export defaults
        if not submission.params_file.is_file():
            TDE17BenchmarkParams().export(submission.params_file)

        return submission

    def load_parameters(self) -> "TDE17BenchmarkParams":
        if self.params_file.is_file():
            obj = load_obj(self.params_file)
            return TDE17BenchmarkParams.parse_obj(obj)
        return TDE17BenchmarkParams()

    def __validate_submission__(self):
        """ Run validation on the submission data """
        self.validation_output = TDE17SubmissionValidation().validate(self)

    @classmethod
    def init_dir(cls, location: Path):
        # create sub-directories
        location.mkdir(exist_ok=True, parents=True)
        # create necessary files
        (location / 'english.txt').touch(exist_ok=True)
        (location / 'french.txt').touch(exist_ok=True)
        (location / 'mandarin.txt').touch(exist_ok=True)
        (location / 'german.txt').touch(exist_ok=True)
        (location / 'wolof.txt').touch(exist_ok=True)
        # scores dir
        (location / 'scores').mkdir(exist_ok=True, parents=True)
        # create params template
        TDE17BenchmarkParams().export(location / TDE17BenchmarkParams.file_stem)
        # create meta template
        template = MetaFile.to_template(benchmark_name="tde17")
        template.to_yaml(
            file=location / MetaFile.file_stem,
            excluded={
                "file_stem": True,
                "model_info": {"model_id"},
                "publication": {"bib_reference", "DOI"}
            }
        )
        instruction_file = Path(__file__).parent / "instructions.md"
        if instruction_file.is_file():
            shutil.copy(instruction_file, location / 'help.md')

    def __zippable__(self):
        return [
            ("", self.meta_file),
            ("", self.params_file),
            *[("", self.location / f"{f}.txt") for f in self.tasks],
            *[("scores/", f) for f in self.score_dir.iterdir()]
        ]
