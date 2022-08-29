import abc
from typing import Dict, Any

from pydantic import BaseModel, DirectoryPath

from .leaderboard import LeaderboardEntry


class ScoreDir(BaseModel, abc.ABC):
    location: DirectoryPath
    output_files: Dict[str, Any]

    @property
    def leaderboard_file(self):
        return self.location / 'leaderboard.json'

    @abc.abstractmethod
    def build_leaderboard(self) -> LeaderboardEntry:
        pass
