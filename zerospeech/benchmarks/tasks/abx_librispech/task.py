import abc
import argparse
from typing import Optional, Tuple, Dict

import libriabx
import pandas as pd
from vdataset import mount, unmount

from .params import ABXParameters, ABXMode, ABXDistanceMode
from ....model import m_benchmark, m_data_items
from ....settings import get_settings

st = get_settings()

default_params = ABXParameters()


extract_return_type = Tuple[str, m_data_items.FileListItem, m_data_items.FileItem]


class SimpleABXTask(m_benchmark.Task, abc.ABC):
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

    @abc.abstractmethod
    def extract_sets(self, submission: m_benchmark.Submission, dataset: m_benchmark.Dataset) -> extract_return_type:
        """ Extract relevant data for abx from submission & dataset """
        pass

    @abc.abstractmethod
    def format_results(self, results: Dict) -> pd.DataFrame:
        """ Format the results as a dataframe """
        pass

    def eval(self, submission: m_benchmark.Submission, dataset: m_benchmark.Dataset):
        """ Simple ABX evaluation """
        output_dir = submission.score_dir
        results = {}

        abx_sets = self.extract_sets(submission, dataset)

        for label, file_list, item_file in abx_sets:
            self.console.print(f'==> Calculating abx distances for {label}')
            results[label] = self.get_abx(
                sub_files=file_list,
                item_file=item_file
            )

        as_df = self.format_results(results)

        filename = output_dir / self.result_filename
        self.console.print(f":pencil: writing {self.result_filename}",
                           style="underline yellow4")
        as_df.to_csv(filename, index=False, float_format='%.4f')
