import json
from enum import Enum
from pathlib import Path
from typing import Optional, Dict, Any, Literal

import yaml

from .....model import m_benchmark


class ABXMode(str, Enum):
    """ ABX mode of computation """
    all = 'all'
    within = 'within'
    across = 'across'

    def as_set(self):
        if self == self.all:
            return self.within, self.across
        else:
            return self,


class ABXDistanceMode(str, Enum):
    """ Enumeration for distance mode for abx algorithm"""
    euclidian = 'euclidian'
    cosine = 'cosine'
    kl = 'kl'
    kl_symmetric = 'kl_symmetric'


FileNameType = Dict[str, Dict[str, str]]
FileTypesTXT = Literal['.npy', '.txt']


class ABXParameters(m_benchmark.BenchmarkParameters):
    # Path to a CPC checkpoint
    path_checkpoint: Optional[str] = None
    # size of a single feature
    feature_size: Optional[float] = float(0.1)
    # Use the GPU to compute distances
    cuda: bool = True
    # Choose the mode of the ABX score to compute
    mode: ABXMode = 'all'
    # Choose the kind of distance to use to compute
    distance_mode: ABXDistanceMode = 'cosine'
    # Max size of a group while computing the ABX score
    max_size_group: int = 10
    # When computing the ABX across score, maximum
    # number of speaker X to sample per couple A,B.
    max_x_across: int = 5
    # location to output the results
    out: Optional[str] = None
    score_file_type: FileTypesTXT = '.npy'
    result_filename: str = "score_phonetic.csv"

    def get_task(self):
        return self.dict()

    def to_meta(self) -> Dict[str, Any]:
        """ Convert into leaderboard meta entry """
        excluded = {'path_checkpoint', 'out', 'result_filename'}
        return dict(self._iter(to_dict=True, exclude=excluded))

    def export(self, file: Path):
        # filtering non-interfaced param values
        excluded = {'path_checkpoint', 'out'}
        # conversion order  self -> json -> pydict -> yaml
        # json is added in before pydict to leverage the pydantic serializer for
        # more complex types as Enum, datetimes, etc. as a simpler chain of
        # self -> pydict -> yaml leaves those unserialised and the yaml serializer fails.
        # see https://pydantic-docs.helpmanual.io/usage/types/#standard-library-types
        as_obj = json.loads(self.json(exclude=excluded))
        with file.open('w') as fp:
            yaml.dump(as_obj, fp)
