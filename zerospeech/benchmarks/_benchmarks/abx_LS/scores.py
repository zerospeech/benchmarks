import uuid
from datetime import datetime
from typing import Optional

from .leaderboard import ABXLSEntry, ABXLSScores, ABXLSScoresSet
from ...tasks.abx_librispech import ABXParameters
from ....data_loaders import load_dataframe
from ....model import m_score_dir, m_leaderboard


class ABXLSScoreDir(m_score_dir.ScoreDir):
    params: Optional[ABXParameters] = ABXParameters()

    @property
    def scores_phonetic(self):
        csv_file = self.location / self.params.result_filename
        return load_dataframe(csv_file)

    def get_details(self) -> m_leaderboard.EntryDetails:
        """ Build entry details """
        train_set = ""
        gpu_budget = ""

        if self.meta_file is not None:
            train_set = self.meta_file.model_info.train_set
            gpu_budget = self.meta_file.model_info.gpu_budget

        return m_leaderboard.EntryDetails(
            train_set=train_set,
            benchmarks=[m_leaderboard.Benchmark.ABX_LS],
            gpu_budget=gpu_budget,
            parameters=self.params.to_meta()
        )

    def get_scores(self) -> ABXLSScores:
        """ Extract & format scores """

        def e(d):
            return {s['type']: s['score'] for s in d}

        frame = self.scores_phonetic
        dev_clean = frame[(frame["dataset"] == 'dev') & (frame["sub-dataset"] == 'clean')][['type', 'score']] \
            .to_dict(orient='records')
        dev_other = frame[(frame["dataset"] == 'dev') & (frame["sub-dataset"] == 'other')][['type', 'score']] \
            .to_dict(orient='records')
        test_clean = frame[(frame["dataset"] == 'test') & (frame["sub-dataset"] == 'clean')][['type', 'score']] \
            .to_dict(orient='records')
        test_other = frame[(frame["dataset"] == 'test') & (frame["sub-dataset"] == 'other')][['type', 'score']] \
            .to_dict(orient='records')

        return ABXLSScores(
            clean=ABXLSScoresSet(
                dev=m_leaderboard.ABXScoreTuple(
                    within=e(dev_clean)['within'],
                    across=e(dev_clean)['across']
                ),
                test=m_leaderboard.ABXScoreTuple(
                    within=e(test_clean)['within'],
                    across=e(test_clean)['across']
                ),
            ),
            other=ABXLSScoresSet(
                dev=m_leaderboard.ABXScoreTuple(
                    within=e(dev_other)['within'],
                    across=e(dev_other)['across']
                ),
                test=m_leaderboard.ABXScoreTuple(
                    within=e(test_other)['within'],
                    across=e(test_other)['across']
                ),
            )
        )

    def build_leaderboard(self) -> ABXLSEntry:
        model_id = ""
        submission_id = str(uuid.uuid4())
        submitted_by = ""
        description = ""

        if self.meta_file is not None:
            model_id = self.meta_file.model_info.model_id
            submitted_by = self.meta_file.username
            description = self.meta_file.model_info.system_description

        return ABXLSEntry(
            model_id=model_id,
            submission_id=submission_id,
            index=-1,
            submission_date=datetime.now(),
            submitted_by=submitted_by,
            description=description,
            publication=self.get_publication_info(),
            scores=self.get_scores(),
            details=self.get_details()
        )
