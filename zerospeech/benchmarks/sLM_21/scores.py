from datetime import datetime
from typing import List

import numpy as np
import pandas as pd

from ...model import m_score_dir
from .leaderboard import (
    SLM21LeaderboardEntry, LexicalScores, ScoreTuple,
    LexicalExtras, SLM21Scores, SemanticScores, SemanticScoreSets, SLM21Extras, SyntacticExtras, SemanticExtras
)
from ...data_loaders import load_dataframe
from ...model import m_leaderboard


class SLM21ScoreDir(m_score_dir.ScoreDir):

    @property
    def lexical_dev_by_pair(self):
        csv_file = self.location / self.output_files['lexical_dev_by_pair']
        return load_dataframe(csv_file)

    @property
    def lexical_test_by_pair(self):
        csv_file = self.location / self.output_files['lexical_test_by_pair']
        return load_dataframe(csv_file)

    @property
    def lexical_dev_by_frequency(self):
        csv_file = self.location / self.output_files['lexical_dev_by_frequency']
        return load_dataframe(csv_file)

    @property
    def lexical_test_by_frequency(self):
        csv_file = self.location / self.output_files['lexical_test_by_frequency']
        return load_dataframe(csv_file)

    @property
    def lexical_dev_by_length(self):
        csv_file = self.location / self.output_files['lexical_dev_by_length']
        return load_dataframe(csv_file)

    @property
    def lexical_test_by_length(self):
        csv_file = self.location / self.output_files['lexical_test_by_length']
        return load_dataframe(csv_file)

    @property
    def semantic_dev_correlation(self):
        csv_file = self.location / self.output_files['semantic_dev_correlation']
        return load_dataframe(csv_file)

    @property
    def semantic_test_correlation(self):
        csv_file = self.location / self.output_files['semantic_test_correlation']
        return load_dataframe(csv_file)

    @property
    def syntactic_dev_by_pair(self):
        csv_file = self.location / self.output_files['syntactic_dev_by_pair']
        return load_dataframe(csv_file)

    @property
    def syntactic_test_by_pair(self):
        csv_file = self.location / self.output_files['syntactic_test_by_pair']
        return load_dataframe(csv_file)

    @property
    def syntactic_dev_by_type(self):
        csv_file = self.location / self.output_files['syntactic_dev_by_type']
        return load_dataframe(csv_file)

    @property
    def syntactic_test_by_type(self):
        csv_file = self.location / self.output_files['syntactic_test_by_type']
        return load_dataframe(csv_file)

    def lexical_scores(self) -> LexicalScores:
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
        frequency_dev = self.lexical_dev_by_frequency
        frequency_test = self.lexical_test_by_frequency

        by_frequency = pd.merge(frequency_dev, frequency_test,
                                how="outer", on=['frequency'], suffixes=("_dev", "_test"))

        length_dev = self.lexical_dev_by_length
        length_test = self.lexical_test_by_length

        by_length = pd.merge(length_dev, length_test, how="outer", on=['length'], suffixes=('_dev', '_test'))

        return LexicalExtras(
            by_length=by_length.to_dict(orient='records'),
            by_frequency=by_frequency.to_dict(orient='records')
        )

    def syntactic_scores(self) -> ScoreTuple:
        return ScoreTuple(dev=1.0, test=1.0)

    def syntactic_extras(self) -> List[SyntacticExtras]:
        return []

    def semantic_scores(self) -> SemanticScores:
        return SemanticScores(
            normal=SemanticScoreSets(
                synthetic=ScoreTuple(dev=1.0, test=1.0),
                librispeech=ScoreTuple(dev=1.0, test=1.0),
            ),
            weighted=SemanticScoreSets(
                synthetic=ScoreTuple(dev=1.0, test=1.0),
                librispeech=ScoreTuple(dev=1.0, test=1.0),
            )
        )

    def semantic_extras(self) -> List[SemanticExtras]:
        return []

    def build_scores(self) -> SLM21Scores:
        return SLM21Scores(
            lexical=self.lexical_scores(),
            syntactic=self.syntactic_scores(),
            semantic=self.semantic_scores()
        )

    def build_extras(self) -> SLM21Extras:
        return SLM21Extras(
            lexical=self.lexical_extras(),
            syntactic=self.syntactic_extras(),
            semantic=self.semantic_extras()
        )

    def get_publication_info(self) -> m_leaderboard.PublicationEntry:
        return m_leaderboard.PublicationEntry(
            institution=""
        )

    def get_details(self) -> m_leaderboard.EntryDetails:
        return m_leaderboard.EntryDetails(
            benchmarks=[m_leaderboard.Benchmark.sLM_21]
        )

    def build_leaderboard(self) -> SLM21LeaderboardEntry:
        return SLM21LeaderboardEntry(
            model_id="",
            submission_id="",
            index=1,
            submission_date=datetime.now(),
            submitted_by="",
            description="",
            publication=self.get_publication_info(),
            details=self.get_details(),
            scores=self.build_scores(),
            extras=self.build_extras()
        )
