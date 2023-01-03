import json
from pathlib import Path
from typing import Optional, Any, Dict

import yaml

from ....model import m_benchmark


class TDE17BenchmarkParams(m_benchmark.BenchmarkParameters):
    """ Parameters for the TDE-17 benchmark """
    # location to output the results
    out: Optional[str] = None
    result_filename: str = "scores.json"

    def get_task(self):
        return self.dict()

    def to_meta(self) -> Dict[str, Any]:
        """ Convert into leaderboard meta entry """
        excluded = {'result_filename', 'out'}
        return dict(self._iter(to_dict=True, exclude=excluded))

    def export(self, file: Path):
        # filtering non-interfaced param values
        excluded = {'result_filename', 'out'}

        # conversion order  self -> json -> pydict -> yaml
        # json is added in before pydict to leverage the pydantic serializer for
        # more complex types as Enum, datetimes, etc. as a simpler chain of
        # self -> pydict -> yaml leaves those unserialised and the yaml serializer fails.
        # see https://pydantic-docs.helpmanual.io/usage/types/#standard-library-types
        as_obj = json.loads(self.json(exclude=excluded))
        with file.open('w') as fp:
            yaml.dump(as_obj, fp)
