import abc
from typing import Optional, Any

from pydantic import BaseModel, DirectoryPath

from zerospeech.leaderboards import LeaderboardEntry, PublicationEntry
from zerospeech.misc import load_obj
from .meta_file import MetaFile


class ScoreDir(BaseModel, abc.ABC):
    submission_dir: DirectoryPath
    location: DirectoryPath
    params: Optional[Any] = None
    meta_file: Optional[MetaFile] = None
    leaderboard_file_name: str = "leaderboard.json"

    def load_meta(self):
        """ Load metadata from submission """
        obj = load_obj(self.submission_dir / MetaFile.file_stem)
        self.meta_file = MetaFile.parse_obj(obj)

    @abc.abstractmethod
    def build_leaderboard(self) -> LeaderboardEntry:
        pass

    def get_publication_info(self) -> PublicationEntry:
        """ Build publication info """
        if self.meta_file is None:
            return PublicationEntry(
                institution=""
            )
        return self.meta_file.get_publication_info()
