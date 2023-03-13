import abc
import json
import shutil
from pathlib import Path
from typing import Optional, List, Iterator, Iterable

import pandas as pd
from Crypto.Hash import MD5
from filesplit.split import Split
from pydantic import BaseModel, Extra, Field


class ManifestIndexItem(BaseModel):
    """ Model representing a file item in the SplitManifest """
    filename: str
    filesize: int
    filehash: Optional[str]

    def __eq__(self, other: 'ManifestIndexItem'):
        return self.filehash == other.filehash

    def __hash__(self):
        return int(self.filehash, 16)

    class Config:
        extra = Extra.ignore  # or 'allow' str


def md5sum(file_path: Path, chunk_size: int = 8192):
    """ Return a md5 hash of a files content """
    h = MD5.new()

    with file_path.open('rb') as f:
        while True:
            chunk = f.read(chunk_size)
            if len(chunk):
                h.update(chunk)
            else:
                break
    return h.hexdigest()


def split_archive(zipfile: Path, chunk_max_size: int = 500000000, hash_parts: bool = True):
    """ Split an archive to multiple paths """

    output_dir = zipfile.parent / f'.{zipfile.stem}.parts'
    output_dir.mkdir(exist_ok=True, parents=True)

    fs = Split(inputfile=str(zipfile), outputdir=str(output_dir))
    fs.bysize(size=chunk_max_size)

    df = pd.read_csv(output_dir / fs.manfilename)
    manifest = [ManifestIndexItem.parse_obj(o) for o in df.to_dict(orient='records')]

    if hash_parts:
        for item in manifest:
            item.filehash = md5sum(output_dir / item.filename)

    return manifest, output_dir


class FileUploadHandler(BaseModel, abc.ABC):
    file: Path
    filehash: str

    @property
    def current_dir(self) -> Path:
        return self.file.parent

    @classmethod
    @abc.abstractmethod
    def _create(cls, target_file: Path):
        """ Abstract method to create manifest """
        pass

    @abc.abstractmethod
    def clean(self):
        """ Clean upload temp files """
        pass

    @staticmethod
    def __resume_path(source: Path):
        """ Path builder to resume file """
        return source.parent / f"{source.stem}.upload.json"

    @property
    def resume_file(self) -> Path:
        """ Current resume file """
        return self.__resume_path(self.file)

    def save(self):
        """ Save progress to disk """
        with self.resume_file.open("w") as fp:
            fp.write(self.json(indent=4))

    @classmethod
    def create_or_load(cls, target_file: Path) -> Optional["FileUploadHandler"]:
        """ Create or load manifest """
        if not target_file.is_file():
            raise FileExistsError(f'{target_file} does not exist')

        if cls.__resume_path(target_file).is_file():
            """ If resume file exists load this instead of recreating it """
            with cls.__resume_path(target_file).open() as fp:
                return cls.parse_obj(json.load(fp))

        # if no resume file build new manifest
        return cls._create(target_file)


class MultipartUploadHandler(FileUploadHandler):
    """ Data Model used for the binary split function as a manifest to allow merging """
    index: Optional[List[ManifestIndexItem]]
    uploaded: List[ManifestIndexItem] = Field(default_factory=list)
    parts_dir: Optional[Path]

    @classmethod
    def _create(cls, target_file: Path):
        """ Build multipart upload manifest """
        file_hash = md5sum(target_file)

        # split file & create upload index
        files_manifest, output_dir = split_archive(target_file)
        manifest = cls(
            file=target_file, filehash=file_hash,
            index=files_manifest, parts_dir=output_dir
        )
        # save to disk to allow resume
        manifest.save()
        return manifest

    def clean(self):
        """ Clean upload temp files """
        self.resume_file.unlink(missing_ok=True)
        shutil.rmtree(self.parts_dir)


class SinglePartUpload(FileUploadHandler):

    @classmethod
    def _create(cls, target_file: Path):
        """ Build singlepart upload manifest """
        return cls(
            file=target_file,
            filehash=md5sum(target_file)
        )

    def clean(self):
        """ Clean upload temp files """
        self.resume_file.unlink(missing_ok=True)
