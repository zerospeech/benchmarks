import abc
import warnings
from pathlib import Path
from typing import Optional, Tuple, Dict, List

import pandas as pd

try:
    import libriabx
except ImportError:
    libriabx = ...
    warnings.warn("abx module not installed")

from .params import ABXParameters, ABXMode, ABXDistanceMode
from .....model import m_benchmark, m_data_items
from .....settings import get_settings
from .....out import warning_console

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

    def abx_args(self, file_list: List[Path], file_ext, item_file):
        """ Build ABX arguments from class attributes """
        if libriabx:
            abx_args = libriabx.AbxArguments.load_from_file_list(
                file_list=file_list,
                path_item_file=str(item_file),
                distance_mode=self.distance_mode,
                feature_size=self.feature_size,
                cuda=self.cuda,
                file_extension=file_ext,
                path_checkpoint=self.path_checkpoint,
                mode=self.mode,
                max_size_group=self.max_size_group,
                max_x_across=self.max_x_across
            )
            # bugfix: _is_mounted is not set by constructor should be fixed in v1.0.6
            abx_args._is_mounted = True
            return abx_args
        else:
            raise ValueError('No abx backend detected')

    def get_abx(self, sub_files: m_data_items.FileListItem, item_file: m_data_items.FileItem) -> Dict[str, float]:
        """  Run abx evaluations on a fileList using a specific .item file

        Returns:
            scores<Dict[str, float]>: where keys represent abx mode (across, within) and float represents the score.
        """
        if None in (sub_files, item_file):
            return {f'{t.value}': '-' for t in self.mode.as_set()}

        arg_obj = self.abx_args(sub_files.files_list, sub_files.file_type.ext, item_file.file)
        if libriabx:
            res = libriabx.abx_eval(arg_obj)
        else:
            raise ValueError('No abx backend detected')

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

        if self.cuda:
            warning_console.print("WARNING: gpu mode is set. You can disable this in the parameters.")

        for label, item_file, file_list in abx_sets:
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
