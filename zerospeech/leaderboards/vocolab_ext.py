import warnings
from pathlib import Path
from typing import Dict, List, Any

from ._models import Leaderboard
from ._types import LeaderboardBenchmarkName
from .abxLS import (
    ABXLSLeaderboard, ABXLSEntry
)
from .exporters import ABXLSExporter, Slm21Exporter, TDE17Exporter
from .sLM21 import (
    SLM21Leaderboard, SLM21LeaderboardEntry
)
from .tde17 import (
    TDE17Leaderboard, TDE17Entry
)

try:
    from vocolab_ext import LeaderboardManager
    from vocolab_ext.leaderboards import LeaderboardEntryBase
except ImportError:
    warnings.warn("vocolab_ext is not installed")

    # Fake variables to prevent errors
    LeaderboardManager = ...
    LeaderboardEntryBase = ...



def get_benchmark(name: str) -> LeaderboardBenchmarkName:
    try:
        return LeaderboardBenchmarkName(name)
    except ValueError:
        raise ValueError("Leaderboard name not found !!!")


class VocolabLeaderboardManager(LeaderboardManager):
    """Class that wraps the usage of leaderboards"""

    def __init__(self, ld: Leaderboard):
        self.leaderboard = ld

    @classmethod
    def load_leaderboard_from_obj(cls, name: str, obj: Dict):
        """Load self from an object"""
        bench = get_benchmark(name)

        if bench == LeaderboardBenchmarkName.ABX_LS:
            return cls(ld=ABXLSLeaderboard.parse_obj(obj))
        elif bench == LeaderboardBenchmarkName.sLM_21:
            return cls(ld=SLM21Leaderboard.parse_obj(obj))
        elif bench == LeaderboardBenchmarkName.TDE_17:
            return cls(ld=TDE17Leaderboard.parse_obj(obj))

        raise TypeError('Unknown leaderboard type')

    @classmethod
    def load_entry_from_obj(cls, name: str, obj: Dict):
        """ Load entry from benchmark name """
        bench = get_benchmark(name)

        if bench == LeaderboardBenchmarkName.ABX_LS:
            return ABXLSEntry.parse_obj(obj)
        elif bench == LeaderboardBenchmarkName.sLM_21:
            return SLM21LeaderboardEntry.parse_obj(obj)
        elif bench == LeaderboardBenchmarkName.TDE_17:
            return TDE17Entry.parse_obj(obj)

        raise TypeError('Unknown leaderboard type')

    @classmethod
    def create_from_entries(cls, name: str, entries: List[Any]):
        """ Create leaderboard from a list of entries"""
        bench = get_benchmark(name)

        if bench == LeaderboardBenchmarkName.ABX_LS:
            return cls(ld=ABXLSLeaderboard(
                data=entries
            ))
        elif bench == LeaderboardBenchmarkName.sLM_21:
            return cls(ld=SLM21Leaderboard(
                data=entries
            ))
        elif bench == LeaderboardBenchmarkName.TDE_17:
            return cls(ld=TDE17Leaderboard(
                data=entries
            ))

    @staticmethod
    def extract_base_from_entry(entry: Any) -> LeaderboardEntryBase:
        publication = getattr(entry, "publication", object())

        return LeaderboardEntryBase(
            submission_id=getattr(entry, "submission_id", ""),
            model_id=getattr(entry, "model_id", ""),
            description=getattr(entry, "description", ""),
            authors=getattr(publication, "authors", ""),
            author_label=getattr(publication, "author_short", None),
            submission_date=getattr(entry, "submission_date", None),
            submitted_by=getattr(entry, "submitted_by", None)
        )

    @staticmethod
    def update_entry_from_base(entry: Any, base: LeaderboardEntryBase):
        entry.submission_id = base.submission_id
        entry.model_id = base.model_id
        entry.description = base.description
        entry.submission_date = base.submission_date
        entry.submitted_by = base.submitted_by
        entry.publication.authors = base.authors
        entry.publication.authors_short = base.author_label
        return entry

    @staticmethod
    def write_entry(entry: Any, file: Path):
        with file.open('w') as fp:
            fp.write(entry.json(ident=4))

    def export_as_csv(self, file: Path):
        """ Export leaderboard into a csv format """
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

    def export_as_json(self, file: Path):
        """ Export leaderboard into a json file """
        with file.open("w") as fp:
            fp.write(self.leaderboard.json(indent=4))
