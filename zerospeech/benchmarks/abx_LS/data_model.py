import argparse
import functools
from pathlib import Path
from typing import Optional, Tuple

import pandas as pd
from vdataset import mount, unmount
import libriabx

from .params import AbxLSBenchmarkParameters, ABXMode, ABXDistanceMode
from ..generic import Submission, ScoresDir, Task
from ...data_items import FileListItem, FileTypes, Item, FileItem
from ...datasets import Dataset, DatasetsDir, DatasetNotFoundError, DatasetNotInstalledError, Namespace
from ...meta_file import MetaFile
from ...misc import load_obj
from ...settings import get_settings

st = get_settings()


class AbxLSDataset(Dataset):
    """ Class interfacing usage of the ABX-LS dataset"""

    @classmethod
    @functools.lru_cache
    def load(cls, load_index: bool = True) -> Optional["AbxLSDataset"]:
        """ Load """
        dataset = DatasetsDir.load().get("abxLS-dataset", cls=cls)

        if dataset is None:
            raise DatasetNotFoundError(f"The abxLS-dataset does not exist")

        if not dataset.installed:
            raise DatasetNotInstalledError("The abxLS-dataset is not installed locally")

        if load_index:
            dataset.load_index()
            # convert all paths to absolute paths
            dataset.index.make_absolute()

        return dataset


class AbxLSSubmission(Submission):
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
                items['dev_clean'] = FileListItem.from_dir(
                    path / 'dev-clean', f_types=[FileTypes.npy, FileTypes.txt]
                )
            if 'test' in sets:
                items['test_clean'] = FileListItem.from_dir(
                    path / 'test-clean', f_types=[FileTypes.npy, FileTypes.txt]
                )

        if 'other' in sets:
            if 'dev' in sets:
                items['dev_other'] = FileListItem.from_dir(
                    path / 'dev-other', f_types=[FileTypes.npy, FileTypes.txt]
                )
            if 'test' in sets:
                items['test_other'] = FileListItem.from_dir(
                    path / 'test-other', f_types=[FileTypes.npy, FileTypes.txt]
                )

        # submission object
        submission = cls(
            sets=sets,
            tasks=tasks,
            meta=MetaFile.from_file(path / 'meta.yaml'),
            location=path,
            items=Namespace[Item](store=items),
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

    # todo implement a check method for ABX-LS submission
    def is_valid(self):
        pass

    def get_scores(self) -> ScoresDir:
        pass


default_params = AbxLSBenchmarkParameters()


class AbxLSTask(Task):
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

    def get_abx(self, sub_files: FileListItem, item_file: FileItem):
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

        if 'dev' is self.sets:
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

        if 'test' is self.sets:
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
