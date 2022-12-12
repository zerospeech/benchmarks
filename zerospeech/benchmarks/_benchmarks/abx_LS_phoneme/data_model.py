import shutil
from pathlib import Path
from typing import Tuple

# from .validators import AbxLSSubmissionValidator
# from ...tasks.abx_librispeech import ABXParameters
from ....misc import load_obj
from ....model import m_benchmark, m_datasets, m_data_items, m_meta_file
from ....settings import get_settings

st = get_settings()


class AbxLSRobSubmission(m_benchmark.Submission):
    """ Submission for ABX-LS-ROB Benchmark """
    sets: Tuple = ('dev', 'test')
    tasks: Tuple = ('clean', 'other')

    @classmethod
    def load(cls, path: Path, *,
             tasks=('clean', 'other'),
             sets=('dev', 'test')):
        """ Load submission for ABX-Ls-ROB benchmark (filter by available tasks & sets) """
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
            items=m_datasets.Namespace[m_data_items.Item](store=items)
        )

        # if params not set export defaults
        if not submission.params_file.is_file():
            # ABXParameters().export(submission.params_file)
            # TODO: define params for libri-abx2
            pass

        return submission

    def load_parameters(self) -> "...":
        if self.params_file.is_file():
            obj = load_obj(self.params_file)
            # todo: define libriabx2 params object
            # return ABXParameters.parse_obj(obj)
        # todo: define libriabx2 params object
        # return ABXParameters()
        return ...

    def __validate_submission__(self):
        """ Run validation on the submission data """
        # todo: define validation for abx-ls-rob
        # self.validation_output = AbxLSSubmissionValidator().validate(self)
        pass

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
        # todo: define params for libriabx2
        # ABXParameters().export(location / ABXParameters.file_stem)
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
