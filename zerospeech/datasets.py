import json
from datetime import datetime
from pathlib import Path
from typing import List, Optional

import requests
from pydantic import BaseModel, DirectoryPath, AnyHttpUrl, validator, parse_obj_as

from .out import console, with_progress
from .settings import get_settings
from .misc import md5sum, unzip

st = get_settings()


class RepositoryItem(BaseModel):
    name: str
    zip_url: AnyHttpUrl
    md5sum: str
    total_size: float

    @validator('zip_url', pre=True)
    def cast_url(cls, v):
        """ Cast strings to AnyHttpUrl """
        if isinstance(v, str):
            return parse_obj_as(AnyHttpUrl, v)
        return v


class RepositoryIndex(BaseModel):
    last_modified: datetime
    datasets: List[RepositoryItem]

    @classmethod
    def load(cls):
        """ Load index from disk """
        with st.repository_index.open() as fp:
            data = json.load(fp)
        return cls(**data)


class Dataset(BaseModel):
    location: Path
    origin: RepositoryItem

    def pull(self, *, verify: bool = True, show_progress: bool = False):
        """ Pull a dataset from remote to the local repository."""
        tmp_dir = st.mkdtemp()
        response = requests.get(self.origin.zip_url, stream=True)

        with with_progress(show=show_progress) as progress:
            task = progress.add_task(f"[red]Downloading {self.location.name}...", total=None)

            with (tmp_dir / f"{self.origin.name}.zip").open("wb") as stream:
                for chunk in response.iter_content(chunk_size=1024):
                    stream.write(chunk)

            progress.update(task, completed=True)

        if verify:
            console.log("Verifying hash...")

        unzip(tmp_dir / f"{self.origin.name}.zip", self.location)


class DatasetsDir(BaseModel):
    root_dir: DirectoryPath

    @classmethod
    def load(cls):
        return cls(root_dir=st.dataset_path)

    @property
    def datasets(self) -> List[str]:
        """ Returns a list of existing datasets """
        return [d.name for d in self.root_dir.iterdir() if d.is_dir()]

    @staticmethod
    def find_repository(dataset_name: str) -> Optional[RepositoryItem]:
        index = RepositoryIndex.load()
        for d in index.datasets:
            if d.name == dataset_name:
                return d
        return None

    def get(self, name) -> Optional[Dataset]:
        loc = self.root_dir / name
        repo = self.find_repository(name)
        if repo is None:
            return None
        return Dataset(location=loc, origin=repo)
