import shutil
from pathlib import Path
from typing import Tuple

from ....misc import load_obj
from ....model import m_benchmark, m_datasets, m_data_items, m_meta_file
from ...tasks.abx.abx_librispeech import ABXParameters


class ABX17Submission(m_benchmark.Submission):
    """ Submission for ABX-17 """
    sets: Tuple = ('1s', '10s', '120s')
    tasks: Tuple = ('english', 'french', 'mandarin', 'german', 'wolof')

    @classmethod
    def load(
            cls, path: Path, *,
            tasks=('english', 'french', 'mandarin', 'german', 'wolof'),
            sets=('1s', '10s', '120s')
    ):
        # submission object
        submission = cls(
            sets=sets,
            tasks=tasks,
            location=path
        )

        # if params not set export defaults
        if not submission.params_file.is_file():
            params = ABXParameters()
            params.result_filename = "scores.csv"
            params.export(submission.params_file)

        # Load items
        file_ext = submission.params.score_file_type.replace('.', '')
        file_ext = m_data_items.FileTypes(file_ext)
        items = dict()

        if 'english' is tasks:
            if '1s' in sets:
                items['english_1s'] = m_data_items.FileListItem.from_dir(
                    path / 'english/1s', f_type=file_ext
                )
            if '10s' in sets:
                items['english_10s'] = m_data_items.FileListItem.from_dir(
                    path / 'english/10s', f_type=file_ext
                )
            if '120s' in sets:
                items['english_120s'] = m_data_items.FileListItem.from_dir(
                    path / 'english/120s', f_type=file_ext
                )
        if 'french' in tasks:
            if '1s' in sets:
                items['french_1s'] = m_data_items.FileListItem.from_dir(
                    path / 'french/1s', f_type=file_ext
                )
            if '10s' in sets:
                items['french_10s'] = m_data_items.FileListItem.from_dir(
                    path / 'french/10s', f_type=file_ext
                )
            if '120s' in sets:
                items['french_120s'] = m_data_items.FileListItem.from_dir(
                    path / 'french/120s', f_type=file_ext
                )
        if 'mandarin' in tasks:
            if '1s' in sets:
                items['mandarin_1s'] = m_data_items.FileListItem.from_dir(
                    path / 'mandarin/1s', f_type=file_ext
                )
            if '10s' in sets:
                items['mandarin_10s'] = m_data_items.FileListItem.from_dir(
                    path / 'mandarin/10s', f_type=file_ext
                )
            if '120s' in sets:
                items['mandarin_120s'] = m_data_items.FileListItem.from_dir(
                    path / 'mandarin/120s', f_type=file_ext
                )
        if 'german' in tasks:
            # retro-compatibility with old format
            gloc = path / 'LANG1'
            if not gloc.is_dir():
                gloc = path / 'german'

            if '1s' in sets:
                items['german_1s'] = m_data_items.FileListItem.from_dir(
                    gloc / '1s', f_type=file_ext
                )
            if '10s' in sets:
                items['german_10s'] = m_data_items.FileListItem.from_dir(
                    gloc / '10s', f_type=file_ext
                )
            if '120s' in sets:
                items['german_120s'] = m_data_items.FileListItem.from_dir(
                    gloc / '120s', f_type=file_ext
                )
        if 'wolof' in tasks:
            # retro-compatibility with old format
            gloc = path / 'LANG2'
            if not gloc.is_dir():
                gloc = path / 'wolof'

            if '1s' in sets:
                items['wolof_1s'] = m_data_items.FileListItem.from_dir(
                    gloc / '1s', f_type=file_ext
                )
            if '10s' in sets:
                items['wolof_10s'] = m_data_items.FileListItem.from_dir(
                    gloc / '10s', f_type=file_ext
                )
            if '120s' in sets:
                items['wolof_120s'] = m_data_items.FileListItem.from_dir(
                    gloc / '120s', f_type=file_ext
                )

        submission.items = m_datasets.Namespace[m_data_items.Item](store=items)
        return submission

    def load_parameters(self) -> "ABXParameters":
        if self.params_file.is_file():
            obj = load_obj(self.params_file)
            return ABXParameters.parse_obj(obj)
        return ABXParameters()

    def __validate_submission__(self):
        """ Run validation on the submission data """
        # TODO make a validator
        pass

    def __zippable__(self):
        return [
            ("", self.meta_file),
            ("", self.params_file),
            *[("english/1s/", f) for f in self.items.english_1s],
            *[("english/10s/", f) for f in self.items.english_10s],
            *[("english/120s/", f) for f in self.items.english_120s],
            *[("french/1s/", f) for f in self.items.french_1s],
            *[("french/10s/", f) for f in self.items.french_10s],
            *[("french/120s/", f) for f in self.items.french_120s],
            *[("mandarin/1s/", f) for f in self.items.mandarin_1s],
            *[("mandarin/10s/", f) for f in self.items.mandarin_10s],
            *[("mandarin/120s/", f) for f in self.items.mandarin_120s],
            *[("german/1s/", f) for f in self.items.german_1s],
            *[("german/10s/", f) for f in self.items.german_10s],
            *[("german/120s/", f) for f in self.items.german_120s],
            *[("wolof/1s/", f) for f in self.items.wolof_1s],
            *[("wolof/10s/", f) for f in self.items.wolof_10s],
            *[("wolof/120s/", f) for f in self.items.wolof_120s],
            *[("scores/", f) for f in self.score_dir.iterdir()]
        ]

    @classmethod
    def init_dir(cls, location: Path):
        # create sub-directories
        location.mkdir(exist_ok=True, parents=True)
        (location / 'english' / "1s").mkdir(exist_ok=True, parents=True)
        (location / 'english' / "10s").mkdir(exist_ok=True, parents=True)
        (location / 'english' / "120s").mkdir(exist_ok=True, parents=True)

        (location / 'french' / "1s").mkdir(exist_ok=True, parents=True)
        (location / 'french' / "10s").mkdir(exist_ok=True, parents=True)
        (location / 'french' / "120s").mkdir(exist_ok=True, parents=True)

        (location / 'mandarin' / "1s").mkdir(exist_ok=True, parents=True)
        (location / 'mandarin' / "10s").mkdir(exist_ok=True, parents=True)
        (location / 'mandarin' / "120s").mkdir(exist_ok=True, parents=True)

        (location / 'german' / "1s").mkdir(exist_ok=True, parents=True)
        (location / 'german' / "10s").mkdir(exist_ok=True, parents=True)
        (location / 'german' / "120s").mkdir(exist_ok=True, parents=True)

        (location / 'wolof' / "1s").mkdir(exist_ok=True, parents=True)
        (location / 'wolof' / "10s").mkdir(exist_ok=True, parents=True)
        (location / 'wolof' / "120s").mkdir(exist_ok=True, parents=True)

        # scores dir
        (location / 'scores').mkdir(exist_ok=True, parents=True)

        # create parameters file
        ABXParameters().export(location / ABXParameters.file_stem)
        # create meta-template
        template = m_meta_file.MetaFile.to_template(benchmark_name="abx17")
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
