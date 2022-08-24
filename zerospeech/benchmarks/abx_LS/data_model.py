import argparse
from pathlib import Path
from typing import Optional, Tuple

import libriabx
import pandas as pd
from vdataset import mount, unmount

from .dataset import AbxLSDataset
from .params import AbxLSBenchmarkParameters, ABXMode, ABXDistanceMode
from .validators import AbxLSSubmissionValidator
from ...misc import load_obj
from ...model import m_benchmark, m_datasets, m_data_items, m_meta_file
from ...settings import get_settings

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

        if 'other' in sets:
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
            meta=m_meta_file.MetaFile.from_file(path / 'meta.yaml'),
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

    def get_scores(self) -> m_benchmark.ScoresDir:
        pass


default_params = AbxLSBenchmarkParameters()


class AbxLSTask(m_benchmark.Task):
    """ Abstract abx-LS task """
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
            ))

    def get_abx(self, sub_files: m_data_items.FileListItem, item_file: m_data_items.FileItem):
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
                results['dev-clean'] = self.get_abx(
                    sub_files=submission.items.dev_clean,
                    item_file=dataset.index.subsets.dev_clean.items.item_file
                )

            if 'other' in self.tasks:
                results['dev-other'] = self.get_abx(
                    sub_files=submission.items.dev_other,
                    item_file=dataset.index.subsets.dev_other.items.item_file
                )

        if 'test' in self.sets:
            if 'clean' in self.tasks:
                results['test-clean'] = self.get_abx(
                    sub_files=submission.items.test_clean,
                    item_file=dataset.index.subsets.test_clean.items.item_file
                )

            if 'other' in self.tasks:
                results['test-other'] = self.get_abx(
                    sub_files=submission.items.test_other,
                    item_file=dataset.index.subsets.test_other.items.item_file
                )

        results = [
            (dset.split('-')[0], dset.split('-')[1], kind, score)
            for dset, v in results.items() for kind, score in v.items()
        ]
        as_df = pd.DataFrame(
            results, columns=['dataset', 'sub-dataset', 'type', 'score']
        )
        filename = output_dir / self.result_filename
        as_df.to_csv(filename, index=False, float_format='%.4f')