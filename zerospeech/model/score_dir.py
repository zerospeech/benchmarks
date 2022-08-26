import abc
from typing import Dict

from pydantic import BaseModel, DirectoryPath

from .leaderboard import LeaderboardEntry


class ScoreDir(BaseModel, abc.ABC):
    location: DirectoryPath
    output_files: Dict[str, str]

    @abc.abstractmethod
    def build_leaderboard(self) -> LeaderboardEntry:
        pass
