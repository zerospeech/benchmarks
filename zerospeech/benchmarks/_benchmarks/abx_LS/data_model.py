import argparse
import shutil
from pathlib import Path
from typing import Optional, Tuple

import libriabx
import pandas as pd
from vdataset import mount, unmount

from .params import AbxLSBenchmarkParameters, ABXMode, ABXDistanceMode
from .validators import AbxLSSubmissionValidator
from ...datasets import AbxLSDataset
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
            AbxLSBenchmarkParameters().export(submission.params_file)

        return submission

    def load_parameters(self) -> "AbxLSBenchmarkParameters":
        if self.params_file.is_file():
            obj = load_obj(self.params_file)
            return AbxLSBenchmarkParameters.parse_obj(obj)
        return AbxLSBenchmarkParameters()

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
        AbxLSBenchmarkParameters().export(location / AbxLSBenchmarkParameters.file_stem)
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


default_params = AbxLSBenchmarkParameters()


class AbxLSTask(m_benchmark.Task):
    """ Abstract abx-LS task """
    _name = "abx-LS"
    # Path to a CPC checkpoint
    path_checkpoint: Optional[str] = default_params.path_checkpoint
    # size of a single feature
    feature_size: Optional[float] = default_params.feature_size
    # Use the GPU to compute distances
    cuda: bool = default_params.cuda
    # Choose the mode of the ABX score to compute
    mode: ABXMode = default_params.mode
    # Choose the kind of distance to use to compute
    distance_mode: ABXDistanceMode = default_params.distance_mode
    # Max size of a group while computing the ABX score
    max_size_group: int = default_params.max_size_group
    # When computing the ABX across score, maximum
    # number of speaker X to sample per couple A,B.
    max_x_across: int = default_params.max_x_across
    # location to output the results
    out: Optional[str] = default_params.out

    sets: Tuple = ('dev', 'test')
    tasks: Tuple = ('clean', 'other')
    result_filename = default_params.result_filename

    def abx_args(self, data_location, file_ext, item_file):
        return argparse.Namespace(
            **dict(
                path_data=str(data_location),
                path_item_file=str(item_file),
                distance_mode=self.distance_mode,
                feature_size=self.feature_size,
                cuda=self.cuda,
                file_extension=file_ext,
                path_checkpoint=self.path_checkpoint,
                mode=self.mode,
                max_size_group=self.max_size_group,
                max_x_across=self.max_x_across
            ))

    def get_abx(self, sub_files: m_data_items.FileListItem, item_file: m_data_items.FileItem):
        if None in (sub_files, item_file):
            return [dict(kind=str(t.value), score='-') for t in self.mode.as_set()]

        data_loc = mount(sub_files.files_list, tmp_prefix=st.TMP_DIR)
        arg_obj = self.abx_args(data_loc, sub_files.file_type.ext, item_file.file)
        res = libriabx.run_abx(arg_obj=arg_obj)
        unmount(data_loc)
        return res

    def eval(self, submission: AbxLSSubmission, dataset: AbxLSDataset):
        """ ABX-LS evaluation of submission  """
        output_dir = submission.score_dir
        self.sets = submission.sets
        self.tasks = submission.tasks
        results = {}

        if 'dev' in self.sets:
            if 'clean' in self.tasks:
                self.console.print('==> Calculating abx distances for dev-clean')
                results['dev-clean'] = self.get_abx(
                    sub_files=submission.items.dev_clean,
                    item_file=dataset.index.subsets.dev_clean.items.item_file
                )

            if 'other' in self.tasks:
                self.console.print('==>Calculating abx distances for dev-other')
                results['dev-other'] = self.get_abx(
                    sub_files=submission.items.dev_other,
                    item_file=dataset.index.subsets.dev_other.items.item_file
                )

        if 'test' in self.sets:
            if 'clean' in self.tasks:
                self.console.print('==> Calculating abx distances for test-clean')
                results['test-clean'] = self.get_abx(
                    sub_files=submission.items.test_clean,
                    item_file=dataset.index.subsets.test_clean.items.item_file
                )

            if 'other' in self.tasks:
                self.console.print('==> Calculating abx distances for test-other')
                results['test-other'] = self.get_abx(
                    sub_files=submission.items.test_other,
                    item_file=dataset.index.subsets.test_other.items.item_file
                )

        results = [
            (dset.split('-')[0], dset.split('-')[1], mode, score)
            for dset, v in results.items() for mode, score in v.items()
        ]
        as_df = pd.DataFrame(
            results, columns=['dataset', 'sub-dataset', 'type', 'score']
        )
        filename = output_dir / self.result_filename
        self.console.print(f":pencil: writing {self.result_filename}",
                           style="underline yellow4")
        as_df.to_csv(filename, index=False, float_format='%.4f')
