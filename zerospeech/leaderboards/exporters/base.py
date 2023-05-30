import abc
from enum import Enum
from pathlib import Path

from pydantic import BaseModel
from zerospeech.leaderboards import Leaderboard


class ExportType(str, Enum):
    csv = 'csv'


class CSVExporter(abc.ABC):

    @abc.abstractmethod
    def to_csv(self):
        pass


class LeaderboardExporter(BaseModel, abc.ABC):
    leaderboard: Leaderboard
    output_file: Path

    def export(self):
        if isinstance(self, CSVExporter):
            self.to_csv()
