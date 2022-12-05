import shutil
from pathlib import Path
from typing import Tuple

from .params import TDE17BenchmarkParams
from ....misc import load_obj
from ....model import m_benchmark, m_datasets, m_data_items, m_meta_file


class TDE17Submission(m_benchmark.Submission):
    """ Submission for TDE-17 """
    sets: Tuple = ('1s', '10s', '120s')
    tasks: Tuple = ('english', 'french', 'mandarin', 'german', 'wolof')

    @classmethod
    def load(
            cls, path: Path, *,
            tasks=('english', 'french', 'mandarin', 'german', 'wolof'),
            sets=('1s', '10s', '120s')
    ):
        items = dict()

        if 'english' in tasks:
            items['english'] = m_data_items.FileItem.from_file(
                path / 'english.txt'
            )

        if 'french' in tasks:
            items['french'] = m_data_items.FileItem.from_file(
                path / 'french.txt'
            )

        if 'mandarin' in tasks:
            items['mandarin'] = m_data_items.FileItem.from_file(
                path / 'mandarin.txt'
            )

        if 'german' in tasks:
            items['german'] = m_data_items.FileItem.from_file(
                path / 'german.txt'
            )

        if 'wolof' in tasks:
            items['wolof'] = m_data_items.FileItem.from_file(
                path / 'wolof.txt'
            )

        submission = cls(
            sets=sets,
            tasks=tasks,
            location=path,
            items=m_datasets.Namespace[m_data_items.Item](store=items)
        )
        # if params not set export defaults
        if not submission.params_file.is_file():
            TDE17BenchmarkParams().export(submission.params_file)

        return submission

    def load_parameters(self) -> "TDE17BenchmarkParams":
        if self.params_file.is_file():
            obj = load_obj(self.params_file)
            return TDE17BenchmarkParams.parse_obj(obj)
        return TDE17BenchmarkParams()

    def __validate_submission__(self):
        """ Run validation on the submission data """
        # TODO: make a validator
        pass

    @classmethod
    def init_dir(cls, location: Path):
        # create sub-directories
        location.mkdir(exist_ok=True, parents=True)
        # create necessary files
        (location / 'english.txt').touch(exist_ok=True)
        (location / 'french.txt').touch(exist_ok=True)
        (location / 'mandarin.txt').touch(exist_ok=True)
        (location / 'german.txt').touch(exist_ok=True)
        (location / 'wolof.txt').touch(exist_ok=True)
        # scores dir
        (location / 'scores').mkdir(exist_ok=True, parents=True)
        # create params template
        TDE17BenchmarkParams().export(location / TDE17BenchmarkParams.file_stem)
        # create meta template
        template = m_meta_file.MetaFile.to_template(benchmark_name="tde17")
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
            *[("", self.location / f"{f}.txt") for f in self.tasks],
            *[("scores/", f) for f in self.score_dir.iterdir()]
        ]
