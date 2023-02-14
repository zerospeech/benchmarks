import functools
import shutil
from pathlib import Path
from typing import Optional

import pandas as pd
from pydantic import Field

from zerospeech import validators, data_loaders
from zerospeech.model import m_benchmark, m_data_items, m_datasets, m_meta_file, m_leaderboard
from zerospeech.misc import load_obj
from ...tasks.lm import ProsodyLMParameters
from ...datasets import ProsAuditLMDataset


class ProsodySubmissionValidation(m_benchmark.SubmissionValidation):
    """ Class that contains all function to validate a ProsAudit Submission"""
    dataset: ProsAuditLMDataset = Field(default_factory=lambda: ProsAuditLMDataset.load())

    @m_benchmark.validation_fn(target="english_dev")
    def validation_english_dev(self, english_dev: m_data_items.FileItem):
        additional_df_checks = [
            # Verify that result df has expected columns
            functools.partial(
                validators.dataframe_column_check, expected_columns=['score']),
            # Verify that result df has all filenames in set
            functools.partial(
                validators.dataframe_index_check,
                expected=[f.stem for f in self.dataset.index.subsets.english_dev.items.wav_list.files_list]
            ),
            # Verify that scores are in float
            functools.partial(
                validators.dataframe_type_check,
                col_name='score',
                expected_type=float
            )
        ]

        # check dataframe
        results = validators.dataframe_check(english_dev, additional_df_checks, sep=' ', header=None,
                                             names=['filename', 'score'], index_col='filename')

        # add item tag
        m_benchmark.add_item('english_dev', results)
        return results

    @m_benchmark.validation_fn(target="english_test")
    def validation_english_dev(self, english_test: m_data_items.FileItem):
        additional_df_checks = [
            # Verify that result df has expected columns
            functools.partial(
                validators.dataframe_column_check, expected_columns=['score']),
            # Verify that result df has all filenames in set
            functools.partial(
                validators.dataframe_index_check,
                expected=[f.stem for f in self.dataset.index.subsets.english_test.items.wav_list.files_list]
            ),
            # Verify that scores are in float
            functools.partial(
                validators.dataframe_type_check,
                col_name='score',
                expected_type=float
            )
        ]

        # check dataframe
        results = validators.dataframe_check(english_test, additional_df_checks, sep=' ', header=None,
                                             names=['filename', 'score'], index_col='filename')

        # add item tag
        m_benchmark.add_item('english_test', results)
        return results


class ProsAuditScoreDir(m_benchmark.ScoreDir):
    params = ProsodyLMParameters

    @property
    def english_dev_score_by_pair(self) -> Optional[pd.DataFrame]:
        csv_file = self.location / self.params.results_filename.format('english', 'dev', 'by_pair')
        if csv_file.is_file():
            return data_loaders.load_dataframe(csv_file)
        return None

    @property
    def english_dev_score_by_type(self) -> Optional[pd.DataFrame]:
        csv_file = self.location / self.params.results_filename.format('english', 'dev', 'by_type')
        if csv_file.is_file():
            return data_loaders.load_dataframe(csv_file)
        return None

    @property
    def english_test_score_by_pair(self) -> Optional[pd.DataFrame]:
        csv_file = self.location / self.params.results_filename.format('english', 'test', 'by_pair')
        if csv_file.is_file():
            return data_loaders.load_dataframe(csv_file)
        return None

    @property
    def english_test_score_by_type(self) -> Optional[pd.DataFrame]:
        csv_file = self.location / self.params.results_filename.format('english', 'test', 'by_type')
        if csv_file.is_file():
            return data_loaders.load_dataframe(csv_file)
        return None

    def build_leaderboard(self) -> m_leaderboard.LeaderboardEntry:
        # todo
        pass


class ProsodySubmission(m_benchmark.Submission):
    sets = ('dev', 'test')
    tasks = ('english',)

    @classmethod
    def load(cls, path: Path, *, sets=('dev', 'test'),
             tasks=('english', 'french', 'japanese')):
        """ Load sLMProsody submission """
        submission = cls(
            sets=sets,
            tasks=tasks,
            location=path
        )

        if not submission.params_file.is_file():
            ProsodyLMParameters().export(submission.params_file)

        items = dict()
        if 'english' in tasks:
            if 'dev' in sets:
                items['english_dev'] = m_data_items.FileItem.from_file(path / 'english_dev.txt')
            if 'test' in sets:
                items['english_test'] = m_data_items.FileItem.from_file(path / 'english_test.txt')

        submission.items = m_datasets.Namespace[m_data_items.Item](store=items)
        return submission

    def __zippable__(self):
        """ Files to include in archive """
        return [
            ("", self.meta_file),
            ("", self.params_file),
            ("", self.items.english_dev.file),
            ("", self.items.english_test.file),
            *[("scores/", f) for f in self.score_dir.iterdir()]
        ]

    @classmethod
    def init_dir(cls, location: Path):
        # create sub-directories
        location.mkdir(exist_ok=True, parents=True)
        (location / 'english_dev.txt').touch(exist_ok=True)
        (location / 'english_test.txt').touch(exist_ok=True)
        # scores dir
        (location / 'scores').mkdir(exist_ok=True, parents=True)
        # create parameters file
        # create meta-template
        template = m_meta_file.MetaFile.to_template(benchmark_name="sLMProsody")
        ProsodyLMParameters().export(location / ProsodyLMParameters.file_stem)
        template.to_yaml(
            file=location / m_meta_file.MetaFile.file_stem,
            excluded={
                "file_stem": True,
                "model_info": {"model_id"},
                "publication": {"bib_reference", "DOI"}
            }
        )
        instruction_file = Path(__file__).parent / "instructions.md"
        if instruction_file.is_file():
            shutil.copy(instruction_file, location / 'help.md')

    def load_parameters(self) -> ProsodyLMParameters:
        if self.params_file.is_file():
            obj = load_obj(self.params_file)
            return ProsodyLMParameters.parse_obj(obj)
        return ProsodyLMParameters()

    def __validate_submission__(self):
        """ Validate that all files are present in submission """
        self.validation_output = ProsodySubmissionValidation().validate(self)

    def get_scores(self) -> ProsAuditScoreDir:
        return ProsAuditScoreDir(
            submission_dir=self.location,
            location=self.score_dir,
            params=self.params
        )
