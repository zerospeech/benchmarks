import shutil
from pathlib import Path
from typing import Tuple, List

from ...tasks.lm import SLM21BenchmarkParameters
from .validators import SLM21SubmissionValidator
from ....misc import load_obj
from ....model import m_benchmark, m_data_items, m_datasets, m_meta_file


class SLM21Submission(m_benchmark.Submission):
    """ Submission for SLM21 Benchmark """
    sets: Tuple = ('dev', 'test')
    tasks: Tuple = ('lexical', 'syntactic', 'semantic')

    @classmethod
    def load(cls, path: Path, *,
             tasks=('lexical', 'syntactic', 'semantic'),
             sets=('dev', 'test')):
        """ Load submission for sLM21 benchmark (filter by available tasks & sets) """
        # submission object
        submission = cls(
            sets=sets,
            tasks=tasks,
            location=path
        )

        # if params not set export defaults
        if not submission.params_file.is_file():
            SLM21BenchmarkParameters().export(submission.params_file)

        # Load items
        items = dict()
        # include lexical task for each set
        if 'lexical' in tasks:
            lexical_dir = path / 'lexical'
            if 'dev' in sets:
                items['lexical_dev'] = m_data_items.FileItem.from_file(lexical_dir / "dev.txt")
            if 'test' in sets:
                items['lexical_test'] = m_data_items.FileItem.from_file(lexical_dir / "test.txt")

        # include syntactic for each set
        if 'syntactic' in tasks:
            syntactic_dir = path / 'syntactic'
            if 'dev' in sets:
                items['syntactic_dev'] = m_data_items.FileItem.from_file(syntactic_dir / "dev.txt")
            if 'test' in sets:
                items['syntactic_test'] = m_data_items.FileItem.from_file(syntactic_dir / "test.txt")

        # include semantic task for each set
        file_ext = submission.params.syntactic.score_files_type.replace('.', '')
        file_ext = m_data_items.FileTypes(file_ext)
        if 'semantic' in tasks:
            semantic_dir = path / 'semantic'
            if 'dev' in sets:
                items['semantic_dev_synthetic'] = m_data_items.FileListItem.from_dir(
                    semantic_dir / "dev/synthetic", f_type=file_ext
                )
                items['semantic_dev_librispeech'] = m_data_items.FileListItem.from_dir(
                    semantic_dir / "dev/librispeech", f_type=file_ext
                )
            if 'test' in sets:
                items['semantic_test_synthetic'] = m_data_items.FileListItem.from_dir(
                    semantic_dir / "test/synthetic", f_type=file_ext
                )
                items['semantic_test_librispeech'] = m_data_items.FileListItem.from_dir(
                    semantic_dir / "test/librispeech", f_type=file_ext
                )

        submission.items = m_datasets.Namespace[m_data_items.Item](store=items)
        return submission

    def __zippable__(self) -> List[Tuple[str, Path]]:
        return [
            ("", self.meta_file),
            ("", self.params_file),
            ("lexical/", self.items.lexical_dev.file),
            ("lexical/", self.items.lexical_test.file),
            ("lexical/", self.items.lexical_test.file),
            ("syntactic/", self.items.syntactic_dev.file),
            ("syntactic/", self.items.syntactic_test.file),
            *[("semantic/dev/synthetic/", f) for f in self.items.semantic_dev_synthetic.files_list],
            *[("semantic/dev/librispeech/", f) for f in self.items.semantic_dev_librispeech.files_list],
            *[("semantic/test/synthetic/", f) for f in self.items.semantic_test_synthetic.files_list],
            *[("semantic/test/librispeech/", f) for f in self.items.semantic_test_librispeech.files_list],
            *[("scores/", f) for f in self.score_dir.iterdir()]
        ]

    @classmethod
    def init_dir(cls, location: Path):
        # create sub-directories
        location.mkdir(exist_ok=True, parents=True)
        (location / 'lexical').mkdir(exist_ok=True, parents=True)
        (location / 'syntactic').mkdir(exist_ok=True, parents=True)
        (location / 'semantic/dev/synthetic').mkdir(exist_ok=True, parents=True)
        (location / 'semantic/dev/librispeech').mkdir(exist_ok=True, parents=True)
        (location / 'semantic/dev/synthetic').mkdir(exist_ok=True, parents=True)
        (location / 'semantic/dev/librispeech').mkdir(exist_ok=True, parents=True)
        # scores dir
        (location / 'scores').mkdir(exist_ok=True, parents=True)
        # create parameters file
        SLM21BenchmarkParameters().export(location / SLM21BenchmarkParameters.file_stem)
        # create meta-template
        template = m_meta_file.MetaFile.to_template(benchmark_name="sLM21")
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
