import json
from enum import Enum
from pathlib import Path
from typing import Optional, Dict, Any, Literal

import yaml

try:
    from zrc_abx2.eval_ABX import SEED
except ImportError:
    # use this default value if variable does not exist
    SEED = 3459

from .....model import m_benchmark


class ABXFileTypes(str, Enum):
    """ Input file type for abx"""
    pt = '.pt'
    npy = '.npy'
    txt = '.txt'
    wav = '.wav'
    flac = '.flac'
    mp3 = '.mp3'


class ABXSpeakerMode(str, Enum):
    """ ABX mode of computation """
    all = 'all'
    within = 'within'
    across = 'across'

    def as_set(self):
        if self == self.all:
            return self.within, self.across
        else:
            return self,


class ContextMode(str, Enum):
    """ ABX context mode of computation """
    all = "all"
    phoneme_any = "phoneme-any"
    phoneme_within = "phoneme-within"
    triphone_within = 'triphone-within'

    def as_set(self):
        if self == self.all:
            return self.phoneme_within, self.phoneme_any, self.triphone_within
        else:
            return self,

    def as_abx2_value(self) -> str:
        if self == self.phoneme_within:
            return "within"
        elif self == self.phoneme_any:
            return "any"
        elif self == self.triphone_within:
            return "within"
        else:
            raise ValueError('Current context has not representable value in abx2 module')


class ABXDistanceMode(str, Enum):
    """ Enumeration for distance mode for abx algorithm"""
    euclidian = 'euclidian'
    cosine = 'cosine'
    kl = 'kl'
    kl_symmetric = 'kl_symmetric'


class PoolingMode(str, Enum):
    """ Pooling method """
    none = "none"
    mean = "mean"
    hamming = "hamming"


FileNameType = Dict[str, Dict[str, str]]
FileTypesTXT = Literal['.npy', '.txt']


class ABX2Parameters(m_benchmark.BenchmarkParameters):
    # Path to a CPC checkpoint
    path_checkpoint: Optional[str] = None
    # size of a single feature
    feature_size: Optional[float] = float(0.1)
    # Use the GPU to compute distances
    cuda: bool = True
    # Choose the mode of the ABX score to compute
    speaker_mode: ABXSpeakerMode = ABXSpeakerMode.all
    # Choose the context type of the ABX score to compute
    context: ContextMode = ContextMode.all
    # Choose the kind of distance to use to compute
    distance_mode: ABXDistanceMode = 'cosine'
    # Max size of a group while computing the ABX score
    max_size_group: int = 10
    # When computing the ABX across score, maximum
    # number of speaker X to sample per couple A,B.
    max_x_across: int = 5
    # Default seed to use
    seed: int = SEED
    # location to output the results
    out: Optional[str] = None
    score_file_type: FileTypesTXT = '.npy'
    result_filename: str = "score_all_phonetic"

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
