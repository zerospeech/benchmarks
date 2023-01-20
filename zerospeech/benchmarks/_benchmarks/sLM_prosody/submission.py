import shutil
from pathlib import Path

from ...tasks.lm import ProsodyLMParameters
from ....misc import load_obj
from ....model import m_benchmark, m_data_items, m_datasets, m_meta_file


class SLMProsodySubmission(m_benchmark.Submission):
    sets = ('dev', 'test')
    tasks = ('english', 'french', 'japanese')

    @classmethod
    def load(cls, path: Path, *, sets=('dev', 'test'),
             tasks=('english', 'french', 'japanese')):
        """ Load sLMProsody submission """
        submission = cls(
            sets=sets,
            tasks=tasks,
            location=path
        )

        if not submission.params_file.is_file():
            ProsodyLMParameters().export(submission.params_file)

        items = dict()
        if 'english' in tasks:
            if 'dev' in sets:
                items['english_dev'] = m_data_items.FileItem.from_file(path / 'english_dev.txt')
            if 'test' in sets:
                items['english_test'] = m_data_items.FileItem.from_file(path / 'english_test.txt')

        if 'french' in tasks:
            if 'dev' in sets:
                items['french_dev'] = m_data_items.FileItem.from_file(path / 'french_dev.txt')
            if 'test' in sets:
                items['french_test'] = m_data_items.FileItem.from_file(path / 'french_test.txt')

        if 'japanese' in tasks:
            if 'dev' in sets:
                items['japanese_dev'] = m_data_items.FileItem.from_file(path / 'japanese_dev.txt')
            if 'test' in sets:
                items['japanese_test'] = m_data_items.FileItem.from_file(path / 'japanese_test.txt')

        submission.items = m_datasets.Namespace[m_data_items.Item](store=items)
        return submission

    def __zippable__(self):
        """ Files to include in archive """
        return [
            ("", self.meta_file),
            ("", self.params_file),
            ("", self.items.english_dev.file),
            ("", self.items.english_test.file),
            ("", self.items.french_dev.file),
            ("", self.items.french_test.file),
            ("", self.items.japanese_dev.file),
            ("", self.items.japanese_test.file),
            *[("scores/", f) for f in self.score_dir.iterdir()]
        ]

    @classmethod
    def init_dir(cls, location: Path):
        # create sub-directories
        location.mkdir(exist_ok=True, parents=True)
        (location / 'english_dev.txt').touch(exist_ok=True)
        (location / 'english_test.txt').touch(exist_ok=True)
        (location / 'french_dev.txt').touch(exist_ok=True)
        (location / 'french_test.txt').touch(exist_ok=True)
        (location / 'japanese_dev.txt').touch(exist_ok=True)
        (location / 'japanese_test.txt').touch(exist_ok=True)
        # scores dir
        (location / 'scores').mkdir(exist_ok=True, parents=True)
        # create parameters file
        # create meta-template
        template = m_meta_file.MetaFile.to_template(benchmark_name="sLMProsody")
        ProsodyLMParameters().export(location / ProsodyLMParameters.file_stem)
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

    def load_parameters(self) -> ProsodyLMParameters:
        if self.params_file.is_file():
            obj = load_obj(self.params_file)
            return ProsodyLMParameters.parse_obj(obj)
        return ProsodyLMParameters()

    def __validate_submission__(self):
        """ Validate that all files are present in submission """
        pass

    def get_scores(self):
        pass
