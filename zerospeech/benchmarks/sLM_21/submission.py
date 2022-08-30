from pathlib import Path
from typing import Tuple

from .params import SLM21BenchmarkParameters
from .validators import SLM21SubmissionValidator
from ...misc import load_obj
from ...model import m_benchmark, m_data_items, m_datasets


class SLM21Submission(m_benchmark.Submission):
    """ Submission for SLM21 Benchmark """
    sets: Tuple = ('dev', 'test')
    tasks: Tuple = ('lexical', 'syntactic', 'semantic')

    @classmethod
    def load(cls, path: Path, score_dir: Path = Path("scores"), *,
             tasks=('lexical', 'syntactic', 'semantic'),
             sets=('dev', 'test')):
        """ Load submission for sLM21 benchmark (filter by available tasks & sets) """
        items = dict()

        # include lexical task for each set
        if 'lexical' in tasks:
            lexical_dir = path / 'lexical'
            if 'dev' in sets:
                items['lexical_dev'] = m_data_items.FileItem.from_file(lexical_dir / "dev.txt")
            if 'test' in sets:
                items['lexical_test'] = m_data_items.FileItem.from_file(lexical_dir / "test.txt")

        # include semantic task for each set
        if 'semantic' in tasks:
            semantic_dir = path / 'semantic'
            if 'dev' in sets:
                items['semantic_dev_synthetic'] = m_data_items.FileListItem.from_dir(
                    semantic_dir / "dev/synthetic", f_types=[m_data_items.FileTypes.npy, m_data_items.FileTypes.txt]
                )
                items['semantic_dev_librispeech'] = m_data_items.FileListItem.from_dir(
                    semantic_dir / "dev/librispeech", f_types=[m_data_items.FileTypes.npy, m_data_items.FileTypes.txt]
                )
            if 'test' in sets:
                items['semantic_test_synthetic'] = m_data_items.FileListItem.from_dir(
                    semantic_dir / "test/synthetic", f_types=[m_data_items.FileTypes.npy, m_data_items.FileTypes.txt]
                )
                items['semantic_test_librispeech'] = m_data_items.FileListItem.from_dir(
                    semantic_dir / "test/librispeech", f_types=[m_data_items.FileTypes.npy, m_data_items.FileTypes.txt]
                )

        # include syntactic for each set
        if 'syntactic' in tasks:
            syntactic_dir = path / 'syntactic'
            if 'dev' in sets:
                items['syntactic_dev'] = m_data_items.FileItem.from_file(syntactic_dir / "dev.txt")
            if 'test' in sets:
                items['syntactic_test'] = m_data_items.FileItem.from_file(syntactic_dir / "test.txt")

        # submission object
        submission = cls(
            sets=sets,
            tasks=tasks,
            location=path,
            items=m_datasets.Namespace[m_data_items.Item](store=items),
            score_dir=score_dir
        )

        # if params not set export defaults
        if not submission.params_file.is_file():
            SLM21BenchmarkParameters().export(submission.params_file)

        return submission

    def load_parameters(self) -> SLM21BenchmarkParameters:
        if self.params_file.is_file():
            obj = load_obj(self.params_file)
            return SLM21BenchmarkParameters.parse_obj(obj)
        return SLM21BenchmarkParameters()

    def __validate_submission__(self):
        """ Run validation on the submission data """
        self.validation_output = SLM21SubmissionValidator().validate(self)

    def get_scores(self):
        pass
