import enum
import functools
import json
from pathlib import Path
from typing import Any, Dict, Literal

import numpy as np
import yaml
from pydantic import BaseModel

from ....model import m_benchmark

FileNameType = Dict[str, Dict[str, str]]

# using metrics from scipy.spatial.distance.cdist
_SciPyMetrics = ['braycurtis', 'canberra', 'chebyshev', 'cityblock', 'correlation', 'cosine', 'dice',
                 'euclidean', 'hamming', 'jaccard', 'jensenshannon', 'kulczynski1', 'mahalanobis',
                 'matching', 'minkowski', 'rogerstanimoto', 'russellrao', 'seuclidean',
                 'sokalmichener', 'sokalsneath', 'sqeuclidean', 'yule']

# Enumeration of metrics used for semantics benchmark
SemanticMetrics = enum.Enum('SemanticMetrics', {f"{k}": k for k in _SciPyMetrics})


class SemanticPooling(str, enum.Enum):
    min = 'min'
    max = 'max'
    mean = 'mean'
    sum = 'sum'
    last = 'last'
    lastlast = 'lastlast'
    off = 'off'

    @property
    def fn(self):
        if self == self.max:
            return functools.partial(np.max, axis=0)
        elif self == self.min:
            return functools.partial(np.min, axis=0)
        elif self == self.mean:
            return functools.partial(np.mean, axis=0)
        elif self == self.sum:
            return functools.partial(np.sum, axis=0)
        elif self == self.last:
            return lambda x: x[-1]
        elif self == self.lastlast:
            return lambda x: x[-2]
        elif self == self.off:
            return lambda x: x
        else:
            raise ValueError(
                f'pooling method must be {",".join([f.value for f in self])}'
            )


class SemanticParams(BaseModel):
    metric: SemanticMetrics = SemanticMetrics('euclidean')
    pooling: SemanticPooling = SemanticPooling.mean
    synthetic: bool = True
    librispeech: bool = True
    correlations: bool = True
    n_jobs: int = 1
    result_filenames: FileNameType = dict(
        dev=dict(
            pairs='score_semantic_dev_pairs.csv',
            correlations='score_semantic_dev_correlation.csv'
        ),
        test=dict(
            pairs='score_semantic_test_pairs.csv',
            correlations='score_semantic_test_correlation.csv'
        )
    )

    class Config:
        json_encoders = {
            SemanticMetrics: lambda x: str(x.value),
        }


class LexicalParams(BaseModel):
    by_pair: bool = True
    by_length: bool = True
    by_frequency: bool = True
    result_filenames: FileNameType = dict(
        dev=dict(
            by_pair='score_lexical_dev_by_pair.csv',
            by_frequency='score_lexical_dev_by_frequency.csv',
            by_length='score_lexical_dev_by_length.csv'
        ),
        test=dict(
            by_pair='score_lexical_test_by_pair.csv',
            by_frequency='score_lexical_test_by_frequency.csv',
            by_length='score_lexical_test_by_length.csv'
        )
    )


FileTypes = Literal['.npy', '.txt']


class SyntacticParams(BaseModel):
    score_files_type: FileTypes = '.npy'
    result_filenames: FileNameType = dict(
        dev=dict(
            by_pair='score_syntactic_dev_by_pair.csv',
            by_type='score_syntactic_dev_by_type.csv'
        ),
        test=dict(
            by_pair='score_syntactic_test_by_pair.csv',
            by_type='score_syntactic_test_by_type.csv'
        )
    )


class SLM21BenchmarkParameters(m_benchmark.BenchmarkParameters):
    lexical: LexicalParams = LexicalParams()
    syntactic: SyntacticParams = SyntacticParams()
    semantic: SemanticParams = SemanticParams()

    def get_lexical(self) -> Dict[str, Any]:
        return {
            "quiet": self.quiet,
            **self.lexical.dict()
        }

    def get_semantic(self) -> Dict[str, Any]:
        return {
            "quiet": self.quiet,
            **self.semantic.dict()
        }

    def get_syntactic(self) -> Dict[str, Any]:
        return {
            "quiet": self.quiet,
            **self.syntactic.dict()
        }

    def to_meta(self) -> Dict[str, Any]:
        """ Convert into leaderboard meta entry """
        # filtering non-interfaced param values
        excluded = {
            'lexical': True,
            'syntactic': True,
            'semantic': {'result_filenames', 'correlations'}
        }

        return dict(self._iter(to_dict=True, exclude=excluded))

    def export(self, file: Path):
        # filtering non-interfaced param values
        excluded = {
            'lexical': True,
            'syntactic': True,
            'semantic': {'result_filenames', 'correlations'}
        }
        # conversion order  self -> json -> pydict -> yaml
        # json is added in before pydict to leverage the pydantic serializer for
        # more complex types as Enum, datetimes, etc. as a simpler chain of
        # self -> pydict -> yaml leaves those unserialised and the yaml serializer fails.
        # see https://pydantic-docs.helpmanual.io/usage/types/#standard-library-types
        as_obj = json.loads(self.json(exclude=excluded))
        with file.open('w') as fp:
            yaml.dump(as_obj, fp)
