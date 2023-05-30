import warnings
from pathlib import Path
from typing import Dict

from ._models import Leaderboard
from ._types import Benchmark
from .benchmarks import (
    ABXLSLeaderboard,
    SLM21Leaderboard,
    TDE17Leaderboard,
)
from .exporters import ABXLSExporter, Slm21Exporter, TDE17Exporter

try:
    from vocolab_ext import LeaderboardManager
except ImportError:
    warnings.warn("vocolab_ext is not installed")

    class LeaderboardManager:
        """Empty class to prevent errors"""

        pass


class VocolabLeaderboardManager(LeaderboardManager):
    """Class that wraps the usage of leaderboards"""

    def __init__(self, ld: Leaderboard):
        self.leaderboard = ld

    @classmethod
    def load_from_obj(cls, name: str, obj: Dict):
        """Load self from an object"""
        try:
            bench = Benchmark(name)
        except ValueError:
            raise ValueError("Leaderboard name not found !!!")

        if bench == Benchmark.ABX_LS:
            return cls(ld=ABXLSLeaderboard.parse_obj(obj))
        elif bench == Benchmark.sLM_21:
            return cls(ld=SLM21Leaderboard.parse_obj(obj))
        elif bench == Benchmark.TDE_17:
            return cls(ld=TDE17Leaderboard.parse_obj(obj))

    def export_as_csv(self, file: Path):
        if isinstance(self.leaderboard, ABXLSLeaderboard):
            exporter = ABXLSExporter(leaderboard=self.leaderboard, output_file=file)
        elif isinstance(self.leaderboard, SLM21Leaderboard):
            exporter = Slm21Exporter(leaderboard=self.leaderboard, output_file=file)
        elif isinstance(self.leaderboard, TDE17Leaderboard):
            exporter = TDE17Exporter(leaderboard=self.leaderboard, output_file=file)
        else:
            raise ValueError("Unknown Leaderboard Type")

        # export to csv
        exporter.to_csv()
