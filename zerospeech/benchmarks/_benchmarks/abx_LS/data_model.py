import shutil
from pathlib import Path
from typing import Tuple

from .validators import AbxLSSubmissionValidator
from ...tasks.abx_librispech import ABXParameters
from ....misc import load_obj
from ....model import m_benchmark, m_datasets, m_data_items, m_meta_file
from ....settings import get_settings

st = get_settings()


class AbxLSSubmission(m_benchmark.Submission):
    """ Submission for ABX-LS Benchmark """
    sets: Tuple = ('dev', 'test')
    tasks: Tuple = ('clean', 'other')

    @classmethod
    def load(cls, path: Path, score_dir: Path = Path("scores"), *,
             tasks=('clean', 'other'),
             sets=('dev', 'test')):
        """ Load submission for ABX-LS benchmark (filter by available tasks & sets)"""
        items = dict()

        if 'clean' in tasks:
            if 'dev' in sets:
                items['dev_clean'] = m_data_items.FileListItem.from_dir(
                    path / 'dev-clean', f_types=[m_data_items.FileTypes.npy, m_data_items.FileTypes.txt]
                )
            if 'test' in sets:
                items['test_clean'] = m_data_items.FileListItem.from_dir(
                    path / 'test-clean', f_types=[m_data_items.FileTypes.npy, m_data_items.FileTypes.txt]
                )

        if 'other' in tasks:
            if 'dev' in sets:
                items['dev_other'] = m_data_items.FileListItem.from_dir(
                    path / 'dev-other', f_types=[m_data_items.FileTypes.npy, m_data_items.FileTypes.txt]
                )
            if 'test' in sets:
                items['test_other'] = m_data_items.FileListItem.from_dir(
                    path / 'test-other', f_types=[m_data_items.FileTypes.npy, m_data_items.FileTypes.txt]
                )

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
            ABXParameters().export(submission.params_file)

        return submission

    def load_parameters(self) -> "ABXParameters":
        if self.params_file.is_file():
            obj = load_obj(self.params_file)
            return ABXParameters.parse_obj(obj)
        return ABXParameters()

    def __validate_submission__(self):
        """ Run validation on the submission data """
        self.validation_output = AbxLSSubmissionValidator().validate(self)

    @classmethod
    def init_dir(cls, location: Path):
        # create sub-directories
        location.mkdir(exist_ok=True, parents=True)
        (location / 'dev-clean').mkdir(exist_ok=True, parents=True)
        (location / 'dev-other').mkdir(exist_ok=True, parents=True)
        (location / 'test-clean').mkdir(exist_ok=True, parents=True)
        (location / 'test-other').mkdir(exist_ok=True, parents=True)
        # create parameters file
        ABXParameters().export(location / ABXParameters.file_stem)
        # create meta-template
        template = m_meta_file.MetaFile.to_template()
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
        ]
