import uuid
from datetime import datetime
from typing import List, Dict, Optional

import numpy as np
import pandas as pd
from pydantic import Extra

from .leaderboard import (
    SLM21LeaderboardEntry, LexicalScores, ScoreTuple,
    LexicalExtras, SLM21Scores, SemanticScores, SemanticScoreSets, SLM21Extras, SyntacticExtras, SemanticExtras
)
from ...datasets import SLM21Dataset
from ...tasks.lm import SLM21BenchmarkParameters
from ....data_loaders import load_dataframe
from ....model import m_leaderboard
from ....model import m_score_dir


class SLM21ScoreDir(m_score_dir.ScoreDir):
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

    def get_details(self) -> m_leaderboard.EntryDetails:
        """ Build entry details """
        train_set = ""
        gpu_budget = ""

        if self.meta_file is not None:
            train_set = self.meta_file.model_info.train_set
            gpu_budget = self.meta_file.model_info.gpu_budget

        return m_leaderboard.EntryDetails(
            train_set=train_set,
            benchmarks=[m_leaderboard.Benchmark.sLM_21],
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
