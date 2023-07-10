import functools
import shutil
from datetime import datetime
from pathlib import Path
from typing import Tuple, Optional, List

import numpy as np
from pydantic import Field

import zerospeech.validators as validators
from zerospeech.data_loaders import load_dataframe
from zerospeech.datasets import AbxLSDataset
from zerospeech.generics import (
    FileListItem, Namespace, Item, FileTypes
)
from zerospeech.leaderboards import EntryDetails, LeaderboardBenchmarkName, LeaderboardEntry
from zerospeech.leaderboards.abxLS import (
    ABXLSEntry, ABXLSScoreSubType
)
from zerospeech.misc import load_obj
from zerospeech.settings import get_settings
from zerospeech.tasks.abx import abx_phoneme
from ._model import ScoreDir, MetaFile, SubmissionValidation, validation_fn, add_item, Submission

st = get_settings()


class AbxLSSubmissionValidator(SubmissionValidation):
    """ File Validation for an ABXLS submission """
    dataset: AbxLSDataset = Field(default_factory=lambda: AbxLSDataset.load())

    @validation_fn(target='dev_clean')
    def validate_dev_clean(self, dev_clean: FileListItem):
        f_list_checks = [
            # Verify that all necessary files are present
            functools.partial(
                validators.file_list_checker,
                expected=self.dataset.index.subsets.dev_clean.items.wav_list.files_list
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
        # Check file list
        results = validators.numpy_array_list_check(
            dev_clean, f_list_checks=f_list_checks, additional_checks=additional_checks
        )
        # add item tag
        add_item('dev_clean', results)
        return results

    @validation_fn(target='dev_other')
    def validate_dev_other(self, dev_other: FileListItem):
        f_list_checks = [
            # Verify that all necessary files are present
            functools.partial(
                validators.file_list_checker,
                expected=self.dataset.index.subsets.dev_other.items.wav_list.files_list
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
        # Check file list
        results = validators.numpy_array_list_check(
            dev_other, f_list_checks=f_list_checks, additional_checks=additional_checks
        )
        # add item tag
        add_item('dev_other', results)
        return results

    @validation_fn(target='test_clean')
    def validate_test_clean(self, test_clean: FileListItem):
        f_list_checks = [
            # Verify that all necessary files are present
            functools.partial(
                validators.file_list_checker,
                expected=self.dataset.index.subsets.test_clean.items.wav_list.files_list
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
        # Check file list
        results = validators.numpy_array_list_check(
            test_clean, f_list_checks=f_list_checks, additional_checks=additional_checks
        )
        # add item tag
        add_item('test_clean', results)
        return results

    @validation_fn(target='test_other')
    def validate_test_other(self, test_other: FileListItem):
        f_list_checks = [
            # Verify that all necessary files are present
            functools.partial(
                validators.file_list_checker,
                expected=self.dataset.index.subsets.test_other.items.wav_list.files_list
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
        # Check file list
        results = validators.numpy_array_list_check(
            test_other, f_list_checks=f_list_checks, additional_checks=additional_checks
        )
        # add item tag
        add_item('test_other', results)
        return results


class ABXLSScoreDir(ScoreDir):
    params: Optional[abx_phoneme.ABX2Parameters] = abx_phoneme.ABX2Parameters()

    @property
    def scores_phonetic(self):
        csv_file = (self.location / self.params.result_filename).with_suffix('.csv')
        return load_dataframe(csv_file)

    def get_details(self) -> EntryDetails:
        """ Build entry details """
        train_set = ""
        gpu_budget = ""

        if self.meta_file is not None:
            train_set = self.meta_file.model_info.train_set
            gpu_budget = self.meta_file.model_info.gpu_budget

        return EntryDetails(
            train_set=train_set,
            benchmarks=[LeaderboardBenchmarkName.ABX_LS],
            gpu_budget=gpu_budget,
            parameters=self.params.to_meta()
        )

    def build_scores(self) -> List[ABXLSScoreSubType]:
        """ Extract & format scores """
        scores = []
        for _, row in self.scores_phonetic.iterrows():
            try:
                seed = int(row['seed'])
            except ValueError:
                seed = None

            scores.append(
                ABXLSScoreSubType(
                    subset=row['subset'],
                    granularity=row['granularity'],
                    speaker_mode=row['speaker_mode'],
                    context_mode=row['context_mode'],
                    score=row['score'],
                    pooling=row['pooling'],
                    seed=seed
                )
            )
        return scores

    def build_meta_data(self):
        """ Build leaderboard metadata """
        return dict(
            model_id=self.meta_file.model_info.model_id,
            submission_id="",
            index=None,
            submission_date=datetime.now(),
            submitted_by=self.meta_file.username,
            description=self.meta_file.model_info.system_description,
            publication=dict(
                author_short=self.meta_file.publication.author_label,
                authors=self.meta_file.publication.authors,
                paper_title=self.meta_file.publication.paper_title,
                paper_ref=self.meta_file.publication.paper_url,
                bib_ref=self.meta_file.publication.bib_reference,
                paper_url=self.meta_file.publication.paper_url,
                pub_year=self.meta_file.publication.publication_year,
                team_name=self.meta_file.publication.team,
                institution=self.meta_file.publication.institution,
                code=self.meta_file.code_url,
                DOI=self.meta_file.publication.DOI,
                open_science=self.meta_file.open_source,
            ),
            details=dict(
                train_set=self.meta_file.model_info.train_set,
                benchmarks=[],
                gpu_budget=self.meta_file.model_info.gpu_budget,
                parameters=self.params.to_meta(),
            )
        )

    def build_leaderboard(self) -> LeaderboardEntry:
        """ Build leaderboard entry for the current submission """
        self.load_meta()

        return ABXLSEntry.parse_obj(
            dict(
                **self.build_meta_data(),
                scores=self.build_scores()
            )
        )


class AbxLSSubmission(Submission):
    """ Submission for ABX-LS-ROB Benchmark """
    sets: Tuple = ('dev', 'test')
    tasks: Tuple = ('clean', 'other')

    @classmethod
    def load(cls, path: Path, *,
             tasks=('clean', 'other'),
             sets=('dev', 'test')):
        """ Load submission for ABX-Ls-ROB benchmark (filter by available tasks & sets) """
        # submission object
        submission = cls(
            sets=sets,
            tasks=tasks,
            location=path
        )

        # if params not set export defaults
        if not submission.params_file.is_file():
            abx_phoneme.ABX2Parameters().export(submission.params_file)

        # Load items
        file_ext = submission.params.score_file_type.replace('.', '')
        file_ext = FileTypes(file_ext)
        items = dict()
        if 'clean' in tasks:
            if 'dev' in sets:
                items['dev_clean'] = FileListItem.from_dir(
                    path / 'dev-clean', f_type=file_ext
                )
            if 'test' in sets:
                items['test_clean'] = FileListItem.from_dir(
                    path / 'test-clean', f_type=file_ext
                )

        if 'other' in tasks:
            if 'dev' in sets:
                items['dev_other'] = FileListItem.from_dir(
                    path / 'dev-other', f_type=file_ext
                )
            if 'test' in sets:
                items['test_other'] = FileListItem.from_dir(
                    path / 'test-other', f_type=file_ext
                )

        submission.items = Namespace[Item](store=items)
        return submission

    def load_parameters(self) -> abx_phoneme.ABX2Parameters:
        if self.params_file.is_file():
            obj = load_obj(self.params_file)
            return abx_phoneme.ABX2Parameters.parse_obj(obj)
        return abx_phoneme.ABX2Parameters()

    def __validate_submission__(self):
        """ Run validation on the submission data """
        self.validation_output = AbxLSSubmissionValidator().validate(self)

    @classmethod
    def init_dir(cls, location: Path):
        """ Create template submission directory """
        # create sub-directories
        location.mkdir(exist_ok=True, parents=True)
        (location / 'dev-clean').mkdir(exist_ok=True, parents=True)
        (location / 'dev-other').mkdir(exist_ok=True, parents=True)
        (location / 'test-clean').mkdir(exist_ok=True, parents=True)
        (location / 'test-other').mkdir(exist_ok=True, parents=True)
        # scores dir
        (location / 'scores').mkdir(exist_ok=True, parents=True)
        # create parameters file
        abx_phoneme.ABX2Parameters().export(location / abx_phoneme.ABX2Parameters.file_stem)
        # create meta-template
        template = MetaFile.to_template(benchmark_name="abxLS")
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
            *[("dev-clean/", f) for f in self.items.dev_clean.files_list],
            *[("dev-other/", f) for f in self.items.dev_other.files_list],
            *[("test-clean/", f) for f in self.items.test_clean.files_list],
            *[("test-other/", f) for f in self.items.test_other.files_list],
            *[("scores/", f) for f in self.score_dir.iterdir()]
        ]

    def get_scores(self):
        """ Load score Dir"""
        return ABXLSScoreDir(
            submission_dir=self.location,
            location=self.score_dir,
            params=self.params
        )
