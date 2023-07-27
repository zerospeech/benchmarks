import functools
import shutil
from pathlib import Path
from typing import Tuple

import numpy as np
import pandas as pd
from pydantic import Field

from zerospeech import validators
from zerospeech.datasets import ZRC2017Dataset
from zerospeech.generics import (
    FileTypes, FileListItem, Namespace, Item, FileItem
)
from zerospeech.misc import load_obj
from zerospeech.tasks.abx.abx17 import ABXParameters
from ._model import MetaFile, Submission, SubmissionValidation, validation_fn, add_item


class ABX17SubmissionValidator(SubmissionValidation):
    """ File Validation for an ABX17 submission"""
    dataset: ZRC2017Dataset = Field(default_factory=lambda: ZRC2017Dataset.load())

    @staticmethod
    def basic_abx_checks(item_list: FileListItem, abx_item: FileItem, tag: str):
        # wav_list are compared to items inside item file
        df = pd.read_csv(abx_item.file, sep=' ')

        f_list_checks = [
            # Verify that all necessary files are present
            functools.partial(
                validators.file_list_stem_check,
                expected=[str(f) for f in df['#file']]
            )
        ]
        additional_checks = [
            # Verify that type of array is float
            functools.partial(
                validators.numpy_dtype_check,
                dtype=np.dtype('float')
            ),
            # Verify that array has 2 dimensions
            functools.partial(
                validators.numpy_dimensions_check,
                ndim=2
            ),
            # Verify that files have the same dimensions
            validators.numpy_col_comparison(1)
        ]
        results = validators.numpy_array_list_check(
            item_list, f_list_checks=f_list_checks, additional_checks=additional_checks
        )
        # add item tag
        add_item(tag, results)
        return results

    @validation_fn(target='english_1s')
    def validate_english_1s(self, english_1s: FileListItem):
        abx_item = self.dataset.index.subsets.english.items.abx_1s_item
        return self.basic_abx_checks(item_list=english_1s, abx_item=abx_item,
                                     tag='english_1s')

    @validation_fn(target='english_10s')
    def validate_english_10s(self, english_10s: FileListItem):
        abx_item = self.dataset.index.subsets.english.items.abx_10s_item
        return self.basic_abx_checks(item_list=english_10s, abx_item=abx_item,
                                     tag='english_10s')

    @validation_fn(target='english_120s')
    def validate_english_120s(self, english_120s: FileListItem):
        abx_item = self.dataset.index.subsets.english.items.abx_120s_item
        return self.basic_abx_checks(item_list=english_120s, abx_item=abx_item,
                                     tag='english_120s')

    @validation_fn(target='french_1s')
    def validate_french_1s(self, french_1s: FileListItem):
        abx_item = self.dataset.index.subsets.french.items.abx_1s_item
        return self.basic_abx_checks(item_list=french_1s, abx_item=abx_item,
                                     tag='french_1s')

    @validation_fn(target='french_10s')
    def validate_french_10s(self, french_10s: FileListItem):
        abx_item = self.dataset.index.subsets.french.items.abx_10s_item
        return self.basic_abx_checks(item_list=french_10s, abx_item=abx_item,
                                     tag='french_10s')

    @validation_fn(target='french_120s')
    def validate_french_120s(self, french_120s: FileListItem):
        abx_item = self.dataset.index.subsets.french.items.abx_120s_item
        return self.basic_abx_checks(item_list=french_120s, abx_item=abx_item,
                                     tag='french_120s')

    @validation_fn(target='mandarin_1s')
    def validate_mandarin_1s(self, mandarin_1s: FileListItem):
        abx_item = self.dataset.index.subsets.mandarin.items.abx_1s_item
        return self.basic_abx_checks(item_list=mandarin_1s, abx_item=abx_item,
                                     tag='mandarin_1s')

    @validation_fn(target='mandarin_10s')
    def validate_mandarin_10s(self, mandarin_10s: FileListItem):
        abx_item = self.dataset.index.subsets.mandarin.items.abx_10s_item
        return self.basic_abx_checks(item_list=mandarin_10s, abx_item=abx_item,
                                     tag='mandarin_10s')

    @validation_fn(target='mandarin_120s')
    def validate_mandarin_120s(self, mandarin_120s: FileListItem):
        abx_item = self.dataset.index.subsets.mandarin.items.abx_120s_item
        return self.basic_abx_checks(item_list=mandarin_120s, abx_item=abx_item,
                                     tag='mandarin_120s')

    @validation_fn(target='german_1s')
    def validate_german_1s(self, german_1s: FileListItem):
        abx_item = self.dataset.index.subsets.german.items.abx_1s_item
        return self.basic_abx_checks(item_list=german_1s, abx_item=abx_item,
                                     tag='german_1s')

    @validation_fn(target='german_10s')
    def validate_german_10s(self, german_10s: FileListItem):
        abx_item = self.dataset.index.subsets.german.items.abx_10s_item
        return self.basic_abx_checks(item_list=german_10s, abx_item=abx_item,
                                     tag='german_10s')

    @validation_fn(target='german_120s')
    def validate_german_120s(self, german_120s: FileListItem):
        abx_item = self.dataset.index.subsets.german.items.abx_120s_item
        return self.basic_abx_checks(item_list=german_120s, abx_item=abx_item,
                                     tag='german_120s')

    @validation_fn(target='wolof_1s')
    def validate_wolof_1s(self, wolof_1s: FileListItem):
        abx_item = self.dataset.index.subsets.wolof.items.abx_1s_item
        return self.basic_abx_checks(item_list=wolof_1s, abx_item=abx_item,
                                     tag='wolof_1s')

    @validation_fn(target='wolof_10s')
    def validate_wolof_10s(self, wolof_10s: FileListItem):
        abx_item = self.dataset.index.subsets.wolof.items.abx_10s_item
        return self.basic_abx_checks(item_list=wolof_10s, abx_item=abx_item,
                                     tag='wolof_10s')

    @validation_fn(target='wolof_120s')
    def validate_wolof_120s(self, wolof_120s: FileListItem):
        abx_item = self.dataset.index.subsets.wolof.items.abx_120s_item
        return self.basic_abx_checks(item_list=wolof_120s, abx_item=abx_item,
                                     tag='wolof_120s')


class ABX17Submission(Submission):
    """ Submission for ABX-17 """
    sets: Tuple = ('1s', '10s', '120s')
    tasks: Tuple = ('english', 'french', 'mandarin', 'german', 'wolof')

    @classmethod
    def load(
            cls, path: Path, *,
            tasks=('english', 'french', 'mandarin', 'german', 'wolof'),
            sets=('1s', '10s', '120s')
    ):
        # submission object
        submission = cls(
            sets=sets,
            tasks=tasks,
            location=path
        )

        # if params not set export defaults
        if not submission.params_file.is_file():
            params = ABXParameters()
            params.result_filename = "scores.csv"
            params.export(submission.params_file)

        # Load items
        file_ext = submission.params.score_file_type.replace('.', '')
        file_ext = FileTypes(file_ext)
        items = dict()

        if 'english' in tasks:
            if '1s' in sets:
                items['english_1s'] = FileListItem.from_dir(
                    path / 'english/1s', f_type=file_ext
                )
            if '10s' in sets:
                items['english_10s'] = FileListItem.from_dir(
                    path / 'english/10s', f_type=file_ext
                )
            if '120s' in sets:
                items['english_120s'] = FileListItem.from_dir(
                    path / 'english/120s', f_type=file_ext
                )
        if 'french' in tasks:
            if '1s' in sets:
                items['french_1s'] = FileListItem.from_dir(
                    path / 'french/1s', f_type=file_ext
                )
            if '10s' in sets:
                items['french_10s'] = FileListItem.from_dir(
                    path / 'french/10s', f_type=file_ext
                )
            if '120s' in sets:
                items['french_120s'] = FileListItem.from_dir(
                    path / 'french/120s', f_type=file_ext
                )
        if 'mandarin' in tasks:
            if '1s' in sets:
                items['mandarin_1s'] = FileListItem.from_dir(
                    path / 'mandarin/1s', f_type=file_ext
                )
            if '10s' in sets:
                items['mandarin_10s'] = FileListItem.from_dir(
                    path / 'mandarin/10s', f_type=file_ext
                )
            if '120s' in sets:
                items['mandarin_120s'] = FileListItem.from_dir(
                    path / 'mandarin/120s', f_type=file_ext
                )
        if 'german' in tasks:
            # retro-compatibility with old format
            gloc = path / 'LANG1'
            if not gloc.is_dir():
                gloc = path / 'german'

            if '1s' in sets:
                items['german_1s'] = FileListItem.from_dir(
                    gloc / '1s', f_type=file_ext
                )
            if '10s' in sets:
                items['german_10s'] = FileListItem.from_dir(
                    gloc / '10s', f_type=file_ext
                )
            if '120s' in sets:
                items['german_120s'] = FileListItem.from_dir(
                    gloc / '120s', f_type=file_ext
                )
        if 'wolof' in tasks:
            # retro-compatibility with old format
            gloc = path / 'LANG2'
            if not gloc.is_dir():
                gloc = path / 'wolof'

            if '1s' in sets:
                items['wolof_1s'] = FileListItem.from_dir(
                    gloc / '1s', f_type=file_ext
                )
            if '10s' in sets:
                items['wolof_10s'] = FileListItem.from_dir(
                    gloc / '10s', f_type=file_ext
                )
            if '120s' in sets:
                items['wolof_120s'] = FileListItem.from_dir(
                    gloc / '120s', f_type=file_ext
                )

        submission.items = Namespace[Item](store=items)
        return submission

    def load_parameters(self) -> "ABXParameters":
        if self.params_file.is_file():
            obj = load_obj(self.params_file)
            return ABXParameters.parse_obj(obj)
        return ABXParameters()

    def __validate_submission__(self):
        """ Run validation on the submission data """
        self.validation_output += ABX17SubmissionValidator().validate(self)

    def __zippable__(self):
        return [
            ("", self.meta_file),
            ("", self.params_file),
            *[("english/1s/", f) for f in self.items.english_1s],
            *[("english/10s/", f) for f in self.items.english_10s],
            *[("english/120s/", f) for f in self.items.english_120s],
            *[("french/1s/", f) for f in self.items.french_1s],
            *[("french/10s/", f) for f in self.items.french_10s],
            *[("french/120s/", f) for f in self.items.french_120s],
            *[("mandarin/1s/", f) for f in self.items.mandarin_1s],
            *[("mandarin/10s/", f) for f in self.items.mandarin_10s],
            *[("mandarin/120s/", f) for f in self.items.mandarin_120s],
            *[("german/1s/", f) for f in self.items.german_1s],
            *[("german/10s/", f) for f in self.items.german_10s],
            *[("german/120s/", f) for f in self.items.german_120s],
            *[("wolof/1s/", f) for f in self.items.wolof_1s],
            *[("wolof/10s/", f) for f in self.items.wolof_10s],
            *[("wolof/120s/", f) for f in self.items.wolof_120s],
            *[("scores/", f) for f in self.score_dir.iterdir()]
        ]

    @classmethod
    def init_dir(cls, location: Path):
        # create sub-directories
        location.mkdir(exist_ok=True, parents=True)
        (location / 'english' / "1s").mkdir(exist_ok=True, parents=True)
        (location / 'english' / "10s").mkdir(exist_ok=True, parents=True)
        (location / 'english' / "120s").mkdir(exist_ok=True, parents=True)

        (location / 'french' / "1s").mkdir(exist_ok=True, parents=True)
        (location / 'french' / "10s").mkdir(exist_ok=True, parents=True)
        (location / 'french' / "120s").mkdir(exist_ok=True, parents=True)

        (location / 'mandarin' / "1s").mkdir(exist_ok=True, parents=True)
        (location / 'mandarin' / "10s").mkdir(exist_ok=True, parents=True)
        (location / 'mandarin' / "120s").mkdir(exist_ok=True, parents=True)

        (location / 'german' / "1s").mkdir(exist_ok=True, parents=True)
        (location / 'german' / "10s").mkdir(exist_ok=True, parents=True)
        (location / 'german' / "120s").mkdir(exist_ok=True, parents=True)

        (location / 'wolof' / "1s").mkdir(exist_ok=True, parents=True)
        (location / 'wolof' / "10s").mkdir(exist_ok=True, parents=True)
        (location / 'wolof' / "120s").mkdir(exist_ok=True, parents=True)

        # scores dir
        (location / 'scores').mkdir(exist_ok=True, parents=True)

        # create parameters file
        ABXParameters().export(location / ABXParameters.file_stem)
        # create meta-template
        template = MetaFile.to_template(benchmark_name="abx17")
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
