import shutil
from datetime import datetime
from pathlib import Path
from typing import Tuple, Optional, List

from zerospeech.benchmarks.tasks.abx import abx_phoneme
from zerospeech.data_loaders import load_dataframe
from zerospeech.misc import load_obj
from zerospeech.model import (
    m_benchmark, m_datasets, m_data_items, m_meta_file, m_leaderboard, m_score_dir
)
from zerospeech.settings import get_settings
from .leaderboard import ABXLSEntry, ABXLSScore
from .validators import AbxLSSubmissionValidator

st = get_settings()


class ABXLSScoreDir(m_score_dir.ScoreDir):
    params: Optional[abx_phoneme.ABX2Parameters] = abx_phoneme.ABX2Parameters()

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

    def build_scores(self) -> List[ABXLSScore]:
        """ Extract & format scores """
        scores = []
        for _, row in self.scores_phonetic.iterrows():
            try:
                seed = int(row['seed'])
            except ValueError:
                seed = None

            scores.append(
                ABXLSScore(
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

    def build_leaderboard(self) -> m_leaderboard.LeaderboardEntry:
        """ Build leaderboard entry for the current submission """
        self.load_meta()

        return ABXLSEntry.parse_obj(
            dict(
                **self.build_meta_data(),
                scores=self.build_scores()
            )
        )


class AbxLSSubmission(m_benchmark.Submission):
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
        file_ext = m_data_items.FileTypes(file_ext)
        items = dict()
        if 'clean' in tasks:
            if 'dev' in sets:
                items['dev_clean'] = m_data_items.FileListItem.from_dir(
                    path / 'dev-clean', f_type=file_ext
                )
            if 'test' in sets:
                items['test_clean'] = m_data_items.FileListItem.from_dir(
                    path / 'test-clean', f_type=file_ext
                )

        if 'other' in tasks:
            if 'dev' in sets:
                items['dev_other'] = m_data_items.FileListItem.from_dir(
                    path / 'dev-other', f_type=file_ext
                )
            if 'test' in sets:
                items['test_other'] = m_data_items.FileListItem.from_dir(
                    path / 'test-other', f_type=file_ext
                )

        submission.items = m_datasets.Namespace[m_data_items.Item](store=items)
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
        template = m_meta_file.MetaFile.to_template(benchmark_name="abxLS")
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
