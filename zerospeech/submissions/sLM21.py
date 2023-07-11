import functools
import shutil
import uuid
from datetime import datetime
from pathlib import Path
from typing import Tuple, List, Optional, Dict

import numpy as np
import pandas as pd
from pydantic import Extra, Field

import zerospeech.validators as validators
from zerospeech.data_loaders import load_dataframe
from zerospeech.datasets import SLM21Dataset
from zerospeech.generics import (
    FileItem, Namespace, Item, FileListItem, FileTypes
)
from zerospeech.leaderboards import EntryDetails, LeaderboardBenchmarkName
from zerospeech.leaderboards.sLM21 import (
    SLM21LeaderboardEntry, LexicalScores, ScoreTuple,
    LexicalExtras, SLM21Scores, SemanticScores,
    SemanticScoreSets, SLM21Extras, SyntacticExtras,
    SemanticExtras
)
from zerospeech.misc import load_obj
from zerospeech.tasks.lm import SLM21BenchmarkParameters
from ._model import MetaFile, ScoreDir, SubmissionValidation, validation_fn, add_item, Submission


class SLM21SubmissionValidator(SubmissionValidation):
    """ Class that contains all functions to validate a sLM21 submission """
    dataset: SLM21Dataset = Field(default_factory=lambda: SLM21Dataset.load())

    @validation_fn(target='lexical_dev')
    def validating_lexical_dev(self, lexical_dev: FileItem):
        additional_df_checks = [
            # Verify that result df has expected columns
            functools.partial(
                validators.dataframe_column_check, expected_columns=['score']),
            # Verify that result df has all filenames in set
            functools.partial(
                validators.dataframe_index_check,
                expected=[f.stem for f in self.dataset.index.subsets.lexical_dev.items.wav_list.files_list]
            ),
            # Verify that scores are in float
            functools.partial(
                validators.dataframe_type_check,
                col_name='score',
                expected_type=float
            )
        ]

        # check dataframe
        results = validators.dataframe_check(lexical_dev, additional_df_checks, sep=' ', header=None,
                                             names=['filename', 'score'], index_col='filename')

        # add item tag
        add_item('lexical_dev', results)
        return results

    @validation_fn(target='lexical_test')
    def validating_lexical_test(self, lexical_test: FileItem):
        # check that file is a correct space separated list with two columns
        additional_df_checks = [
            # Verify that result df has expected columns
            functools.partial(
                validators.dataframe_column_check, expected_columns=['score']),
            # Verify that result df has all filenames in set
            functools.partial(
                validators.dataframe_index_check,
                expected=[f.stem for f in self.dataset.index.subsets.lexical_test.items.wav_list.files_list]
            ),
            # Verify that scores are in float
            functools.partial(
                validators.dataframe_type_check,
                col_name='score',
                expected_type=float
            )
        ]

        # check dataframe
        results = validators.dataframe_check(lexical_test, additional_df_checks, sep=' ', header=None,
                                             names=['filename', 'score'], index_col='filename')

        # add item tag
        add_item('lexical_test', results)
        return results

    @validation_fn(target='semantic_dev_synthetic')
    def validating_semantic_dev_synthetic(self, semantic_dev_synthetic: FileListItem):
        f_list_checks = [
            # Verify that all necessary files are present
            functools.partial(
                validators.file_list_checker,
                expected=self.dataset.index.subsets.semantic_dev.items.synthetic_wav_list.files_list
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
            )
        ]

        # Check file list
        results = validators.numpy_array_list_check(
            semantic_dev_synthetic, f_list_checks=f_list_checks, additional_checks=additional_checks
        )

        # add item tag
        add_item('semantic_dev_synthetic', results)
        return results

    @validation_fn(target='semantic_dev_librispeech')
    def validating_semantic_dev_librispeech(self, semantic_dev_librispeech: FileListItem):
        f_list_checks = [
            # Verify that all necessary files are present
            functools.partial(
                validators.file_list_checker,
                expected=self.dataset.index.subsets.semantic_dev.items.librispeech_wav_list.files_list
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
            )
        ]

        # Check file list
        results = validators.numpy_array_list_check(
            semantic_dev_librispeech, f_list_checks=f_list_checks, additional_checks=additional_checks
        )

        # add item tag
        add_item('semantic_dev_librispeech', results)
        return results

    @validation_fn(target='semantic_test_synthetic')
    def validating_semantic_test_synthetic(self, semantic_test_synthetic: FileListItem):
        f_list_checks = [
            # Verify that all necessary files are present
            functools.partial(
                validators.file_list_checker,
                expected=self.dataset.index.subsets.semantic_test.items.synthetic_wav_list.files_list
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
            )
        ]

        # Check file list
        results = validators.numpy_array_list_check(
            semantic_test_synthetic, f_list_checks=f_list_checks, additional_checks=additional_checks
        )

        # add item tag
        add_item('semantic_test_synthetic', results)
        return results

    @validation_fn(target='semantic_test_librispeech')
    def validating_semantic_test_librispeech(self, semantic_test_librispeech: FileListItem):
        f_list_checks = [
            # Verify that all necessary files are present
            functools.partial(
                validators.file_list_checker,
                expected=self.dataset.index.subsets.semantic_test.items.librispeech_wav_list.files_list
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
            )
        ]

        # Check file list
        results = validators.numpy_array_list_check(
            semantic_test_librispeech, f_list_checks=f_list_checks, additional_checks=additional_checks
        )

        # add item tag
        add_item('semantic_test_librispeech', results)
        return results

    @validation_fn(target='syntactic_dev')
    def validating_syntactic_dev(self, syntactic_dev: FileItem):
        additional_df_checks = [
            # Verify that result df has expected columns
            functools.partial(
                validators.dataframe_column_check, expected_columns=['score']),
            # Verify that result df has all filenames in set
            functools.partial(
                validators.dataframe_index_check,
                expected=[f.stem for f in self.dataset.index.subsets.syntactic_dev.items.wav_list.files_list]
            ),
            # Verify that scores are in float
            functools.partial(
                validators.dataframe_type_check,
                col_name='score',
                expected_type=float
            )
        ]

        # check dataframe
        results = validators.dataframe_check(syntactic_dev, additional_df_checks, sep=' ', header=None,
                                             names=['filename', 'score'], index_col='filename')

        # add item tag
        add_item('syntactic_dev', results)
        return results

    @validation_fn(target='syntactic_test')
    def validating_syntactic_test(self, syntactic_test: FileItem):
        additional_df_checks = [
            # Verify that result df has expected columns
            functools.partial(
                validators.dataframe_column_check, expected_columns=['score']),
            # Verify that result df has all filenames in set
            functools.partial(
                validators.dataframe_index_check,
                expected=[f.stem for f in self.dataset.index.subsets.syntactic_test.items.wav_list.files_list]
            ),
            # Verify that scores are in float
            functools.partial(
                validators.dataframe_type_check,
                col_name='score',
                expected_type=float
            )
        ]

        # check dataframe
        results = validators.dataframe_check(syntactic_test, additional_df_checks, sep=' ', header=None,
                                             names=['filename', 'score'], index_col='filename')

        # add item tag
        add_item('syntactic_test', results)
        return results


class SLM21ScoreDir(ScoreDir):
    """ Data representation of the sLM21 scores directory """
    params: Optional[SLM21BenchmarkParameters] = SLM21BenchmarkParameters()

    class Config:
        arbitrary_types_allowed = Extra.ignore

    @property
    def semantic_size(self) -> Dict[str, pd.DataFrame]:
        """ Get semantic size from original dataset """
        dataset = SLM21Dataset.load()
        dev_size = pd.read_csv(dataset.index.subsets.semantic_dev.items.pairs.file, header=0) \
            .groupby(['type', 'dataset'], as_index=False).size()
        test_size = pd.read_csv(dataset.index.subsets.semantic_test.items.pairs.file, header=0) \
            .groupby(['type', 'dataset'], as_index=False).size()

        return dict(dev=dev_size, test=test_size)

    @property
    def lexical_dev_by_pair(self):
        csv_file = self.location / self.params.lexical.result_filenames['dev']['by_pair']
        return load_dataframe(csv_file)

    @property
    def lexical_test_by_pair(self):
        csv_file = self.location / self.params.lexical.result_filenames['test']['by_pair']
        return load_dataframe(csv_file)

    @property
    def lexical_dev_by_frequency(self):
        csv_file = self.location / self.params.lexical.result_filenames['dev']['by_frequency']
        return load_dataframe(csv_file)

    @property
    def lexical_test_by_frequency(self):
        csv_file = self.location / self.params.lexical.result_filenames['test']['by_frequency']
        return load_dataframe(csv_file)

    @property
    def lexical_dev_by_length(self):
        csv_file = self.location / self.params.lexical.result_filenames['dev']['by_length']
        return load_dataframe(csv_file)

    @property
    def lexical_test_by_length(self):
        csv_file = self.location / self.params.lexical.result_filenames['test']['by_length']
        return load_dataframe(csv_file)

    @property
    def semantic_dev_correlation(self):
        csv_file = self.location / self.params.semantic.result_filenames['dev']['correlations']
        return load_dataframe(csv_file)

    @property
    def semantic_test_correlation(self):
        csv_file = self.location / self.params.semantic.result_filenames['test']['correlations']
        return load_dataframe(csv_file)

    @property
    def syntactic_dev_by_pair(self):
        csv_file = self.location / self.params.syntactic.result_filenames['dev']['by_pair']
        return load_dataframe(csv_file)

    @property
    def syntactic_test_by_pair(self):
        csv_file = self.location / self.params.syntactic.result_filenames['test']['by_pair']
        return load_dataframe(csv_file)

    @property
    def syntactic_dev_by_type(self):
        csv_file = self.location / self.params.syntactic.result_filenames['dev']['by_type']
        return load_dataframe(csv_file)

    @property
    def syntactic_test_by_type(self):
        csv_file = self.location / self.params.syntactic.result_filenames['test']['by_type']
        return load_dataframe(csv_file)

    def lexical_scores(self) -> LexicalScores:
        """ Extract lexical resume of scores """
        dev_score = self.lexical_dev_by_pair['score'].mean()
        test_score = self.lexical_test_by_pair['score'].mean()

        def _score_invocab(frame):
            # filter out OOVs
            frame = frame[frame['frequency'] != 'oov']
            # weighted mean
            return np.average(
                frame['score'].to_numpy(),
                weights=frame['n'].to_numpy())

        # weighted scores
        dev_invocab = _score_invocab(self.lexical_dev_by_frequency)
        test_invocab = _score_invocab(self.lexical_test_by_frequency)
        return LexicalScores(
            all=ScoreTuple(dev=dev_score, test=test_score),
            in_vocab=ScoreTuple(dev=dev_invocab, test=test_invocab)
        )

    def lexical_extras(self):
        """ Extract lexical detailed scores """
        frequency_dev = self.lexical_dev_by_frequency
        frequency_test = self.lexical_test_by_frequency

        by_frequency = pd.merge(frequency_dev, frequency_test,
                                how="outer", on=['frequency'], suffixes=("_dev", "_test"))

        length_dev = self.lexical_dev_by_length
        length_test = self.lexical_test_by_length

        by_length = pd.merge(length_dev, length_test, how="outer", on=['length'], suffixes=('_dev', '_test'))

        return LexicalExtras.parse_obj(dict(
            by_length=by_length.to_dict(orient='records'),
            by_frequency=by_frequency.to_dict(orient='records')
        ))

    def syntactic_scores(self) -> ScoreTuple:
        """ Extract syntactic score resume """
        dev_mean = self.syntactic_dev_by_pair['score'].mean()
        test_mean = self.syntactic_test_by_pair['score'].mean()
        return ScoreTuple(dev=dev_mean, test=test_mean)

    def syntactic_extras(self) -> List[SyntacticExtras]:
        """ Extract syntactic detailed scores """
        dev_types = self.syntactic_dev_by_type
        test_types = self.syntactic_test_by_type

        # merge
        merged = pd.merge(dev_types, test_types, how="outer", on=["type"], suffixes=("_dev", "_test"))
        merged.rename(columns={'type': 'typeset'}, inplace=True)

        return [SyntacticExtras(**se) for se in merged.to_dict(orient='records')]

    def semantic_scores(self) -> SemanticScores:
        """ Extract semantic score resume """
        dev_correlations = self.semantic_dev_correlation
        test_correlations = self.semantic_test_correlation

        # Mean
        dev_librispeech_mean = dev_correlations[dev_correlations['type'] == 'librispeech']['correlation'].mean()
        dev_synthetic_mean = dev_correlations[dev_correlations['type'] == 'synthetic']['correlation'].mean()
        test_librispeech_mean = test_correlations[test_correlations['type'] == 'librispeech']['correlation'].mean()
        test_synthetic_mean = test_correlations[test_correlations['type'] == 'synthetic']['correlation'].mean()

        # Weighted Mean
        semantic_size = self.semantic_size

        dev_correlations['size'] = semantic_size['dev']['size']
        dev_librispeech_wmean = np.average(
            dev_correlations[dev_correlations['type'] == 'librispeech']['correlation'].to_numpy(),
            weights=dev_correlations[dev_correlations['type'] == 'librispeech']['size'].to_numpy())
        dev_synthetic_wmean = np.average(
            dev_correlations[dev_correlations['type'] == 'synthetic']['correlation'].to_numpy(),
            weights=dev_correlations[dev_correlations['type'] == 'synthetic']['size'].to_numpy())

        test_correlations['size'] = semantic_size['test']['size']
        test_librispeech_wmean = np.average(
            test_correlations[test_correlations['type'] == 'librispeech']['correlation'].to_numpy(),
            weights=test_correlations[test_correlations['type'] == 'librispeech']['size'].to_numpy())
        test_synthetic_wmean = np.average(
            test_correlations[test_correlations['type'] == 'synthetic']['correlation'].to_numpy(),
            weights=test_correlations[test_correlations['type'] == 'synthetic']['size'].to_numpy())

        return SemanticScores(
            normal=SemanticScoreSets(
                synthetic=ScoreTuple(dev=dev_synthetic_mean, test=test_synthetic_mean),
                librispeech=ScoreTuple(dev=dev_librispeech_mean, test=test_librispeech_mean),
            ),
            weighted=SemanticScoreSets(
                synthetic=ScoreTuple(dev=dev_synthetic_wmean, test=test_synthetic_wmean),
                librispeech=ScoreTuple(dev=dev_librispeech_wmean, test=test_librispeech_wmean),
            )
        )

    def semantic_extras(self) -> List[SemanticExtras]:
        """ Extract semantic score resume """
        dev_correlations = self.semantic_dev_correlation
        test_correlations = self.semantic_test_correlation

        ndev_correlations = dev_correlations \
            .set_index(['dataset', dev_correlations.groupby('dataset').cumcount()])['correlation'] \
            .unstack() \
            .reset_index()
        ndev_correlations.columns = ['dataset', 'librispeech', 'synthetic']
        ndev_correlations["set"] = "dev"

        ntest_correlations = test_correlations \
            .set_index(['dataset', test_correlations.groupby('dataset').cumcount()])['correlation'] \
            .unstack() \
            .reset_index()
        ntest_correlations.columns = ['dataset', 'librispeech', 'synthetic']
        ntest_correlations["set"] = "test"

        # DeprecationWarning from pandas: append is to be replaced by concat
        correlations = pd.concat([ndev_correlations, ntest_correlations], axis=0)
        # correlations = ndev_correlations.append(ntest_correlations)

        return [SemanticExtras(**se) for se in correlations.to_dict(orient='records')]

    def build_scores(self) -> SLM21Scores:
        """ Extract all score resume """
        return SLM21Scores(
            lexical=self.lexical_scores(),
            syntactic=self.syntactic_scores(),
            semantic=self.semantic_scores()
        )

    def build_extras(self) -> SLM21Extras:
        """ Extract all detailed scores """
        return SLM21Extras(
            lexical=self.lexical_extras(),
            syntactic=self.syntactic_extras(),
            semantic=self.semantic_extras()
        )

    def get_details(self) -> EntryDetails:
        """ Build entry details """
        train_set = ""
        gpu_budget = ""

        if self.meta_file is not None:
            train_set = self.meta_file.model_info.train_set
            gpu_budget = self.meta_file.model_info.gpu_budget

        return EntryDetails(
            train_set=train_set,
            benchmarks=[LeaderboardBenchmarkName.sLM_21],
            gpu_budget=gpu_budget,
            parameters=self.params.to_meta()
        )

    def build_leaderboard(self) -> SLM21LeaderboardEntry:
        """ Build leaderboard entry from calculated scores """
        model_id = ""
        submission_id = str(uuid.uuid4())
        submitted_by = ""
        description = ""

        if self.meta_file is not None:
            model_id = self.meta_file.model_info.model_id
            submitted_by = self.meta_file.username
            description = self.meta_file.model_info.system_description

        return SLM21LeaderboardEntry(
            model_id=model_id,
            submission_id=submission_id,
            index=-1,
            submission_date=datetime.now(),
            submitted_by=submitted_by,
            description=description,
            publication=self.get_publication_info(),
            details=self.get_details(),
            scores=self.build_scores(),
            extras=self.build_extras()
        )


class SLM21Submission(Submission):
    """ Submission for SLM21 Benchmark """
    sets: Tuple = ('dev', 'test')
    tasks: Tuple = ('lexical', 'syntactic', 'semantic')

    @classmethod
    def load(cls, path: Path, *,
             tasks=('lexical', 'syntactic', 'semantic'),
             sets=('dev', 'test')):
        """ Load submission for sLM21 benchmark (filter by available tasks & sets) """
        # submission object
        submission = cls(
            sets=sets,
            tasks=tasks,
            location=path
        )

        # if params not set export defaults
        if not submission.params_file.is_file():
            SLM21BenchmarkParameters().export(submission.params_file)

        # Load items
        items = dict()
        # include lexical task for each set
        if 'lexical' in tasks:
            lexical_dir = path / 'lexical'
            if 'dev' in sets:
                items['lexical_dev'] = FileItem.from_file(lexical_dir / "dev.txt")
            if 'test' in sets:
                items['lexical_test'] = FileItem.from_file(lexical_dir / "test.txt")

        # include syntactic for each set
        if 'syntactic' in tasks:
            syntactic_dir = path / 'syntactic'
            if 'dev' in sets:
                items['syntactic_dev'] = FileItem.from_file(syntactic_dir / "dev.txt")
            if 'test' in sets:
                items['syntactic_test'] = FileItem.from_file(syntactic_dir / "test.txt")

        # include semantic task for each set
        file_ext = submission.params.syntactic.score_files_type.replace('.', '')
        file_ext = FileTypes(file_ext)
        if 'semantic' in tasks:
            semantic_dir = path / 'semantic'
            if 'dev' in sets:
                items['semantic_dev_synthetic'] = FileListItem.from_dir(
                    semantic_dir / "dev/synthetic", f_type=file_ext
                )
                items['semantic_dev_librispeech'] = FileListItem.from_dir(
                    semantic_dir / "dev/librispeech", f_type=file_ext
                )
            if 'test' in sets:
                items['semantic_test_synthetic'] = FileListItem.from_dir(
                    semantic_dir / "test/synthetic", f_type=file_ext
                )
                items['semantic_test_librispeech'] = FileListItem.from_dir(
                    semantic_dir / "test/librispeech", f_type=file_ext
                )

        submission.items = Namespace[Item](store=items)
        return submission

    def __zippable__(self) -> List[Tuple[str, Path]]:
        return [
            ("", self.meta_file),
            ("", self.params_file),
            ("lexical/", self.items.lexical_dev.file),
            ("lexical/", self.items.lexical_test.file),
            ("lexical/", self.items.lexical_test.file),
            ("syntactic/", self.items.syntactic_dev.file),
            ("syntactic/", self.items.syntactic_test.file),
            *[("semantic/dev/synthetic/", f) for f in self.items.semantic_dev_synthetic.files_list],
            *[("semantic/dev/librispeech/", f) for f in self.items.semantic_dev_librispeech.files_list],
            *[("semantic/test/synthetic/", f) for f in self.items.semantic_test_synthetic.files_list],
            *[("semantic/test/librispeech/", f) for f in self.items.semantic_test_librispeech.files_list],
            *[("scores/", f) for f in self.score_dir.iterdir()]
        ]

    @classmethod
    def init_dir(cls, location: Path):
        # create sub-directories
        location.mkdir(exist_ok=True, parents=True)
        (location / 'lexical').mkdir(exist_ok=True, parents=True)
        (location / 'syntactic').mkdir(exist_ok=True, parents=True)
        (location / 'semantic/dev/synthetic').mkdir(exist_ok=True, parents=True)
        (location / 'semantic/dev/librispeech').mkdir(exist_ok=True, parents=True)
        (location / 'semantic/dev/synthetic').mkdir(exist_ok=True, parents=True)
        (location / 'semantic/dev/librispeech').mkdir(exist_ok=True, parents=True)
        # scores dir
        (location / 'scores').mkdir(exist_ok=True, parents=True)
        # create parameters file
        SLM21BenchmarkParameters().export(location / SLM21BenchmarkParameters.file_stem)
        # create meta-template
        template = MetaFile.to_template(benchmark_name="sLM21")
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

    def load_parameters(self) -> SLM21BenchmarkParameters:
        if self.params_file.is_file():
            obj = load_obj(self.params_file)
            return SLM21BenchmarkParameters.parse_obj(obj)
        return SLM21BenchmarkParameters()

    def __validate_submission__(self):
        """ Run validation on the submission data """
        self.validation_output = SLM21SubmissionValidator().validate(self)

    def get_scores(self):
        """ """
        pass
