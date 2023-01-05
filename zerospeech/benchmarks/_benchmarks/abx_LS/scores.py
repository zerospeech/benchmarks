import uuid
from datetime import datetime
from typing import Optional, List

from zerospeech.benchmarks.tasks.abx.abx_phoneme import ABX2Parameters
from zerospeech.data_loaders import load_dataframe
from zerospeech.model import m_score_dir, m_leaderboard
from .leaderboard import ABXLSEntry, ABXLSScore


class ABXLSScoreDir(m_score_dir.ScoreDir):
    params: Optional[ABX2Parameters] = ABX2Parameters()

    @property
    def scores_phonetic(self):
        csv_file = (self.location / self.params.result_filename).with_suffix('.csv')
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

    def get_scores(self) -> List[ABXLSScore]:
        """ Extract & format scores """
        scores = []
        for _, row in self.scores_phonetic.iterrows():
            scores.append(
                ABXLSScore(
                    subset=row['subset'],
                    granularity=row['granularity'],
                    speaker_mode=row['speaker_mode'],
                    context_mode=row['context_mode'],
                    score=row['score'],
                    pooling=row['pooling'],
                    seed=row['seed']
                )
            )
        return scores

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
