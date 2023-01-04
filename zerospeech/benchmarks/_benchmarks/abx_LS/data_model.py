import shutil
from pathlib import Path
from typing import Tuple

from .validators import AbxLSSubmissionValidator
from ...tasks.abx.abx_phoneme import ABX2Parameters
from ....misc import load_obj
from ....model import m_benchmark, m_datasets, m_data_items, m_meta_file
from ....settings import get_settings

st = get_settings()


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
            ABX2Parameters().export(submission.params_file)

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

    def load_parameters(self) -> ABX2Parameters:
        if self.params_file.is_file():
            obj = load_obj(self.params_file)
            return ABX2Parameters.parse_obj(obj)
        return ABX2Parameters()

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
        ABX2Parameters().export(location / ABX2Parameters.file_stem)
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
