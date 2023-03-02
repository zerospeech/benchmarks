import json
from pathlib import Path
from typing import Optional, List

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
            item.file_hash = md5sum(output_dir / item.filename)

    return manifest, output_dir


class MultipartUploadHandler(BaseModel):
    """ Data Model used for the binary split function as a manifest to allow merging """
    file: Path
    filehash: str
    index: Optional[List[ManifestIndexItem]]
    uploaded: List[ManifestIndexItem] = Field(default_factory=list)
    output_dir: Optional[Path]

    @staticmethod
    def resume_file(source: Path) -> Path:
        return source.parent / f"{source.stem}.upload.json"

    def save(self):
        """ Save progress to disk """
        with self.resume_file(self.file).open("w") as fp:
            fp.write(self.json(indent=4))

    @classmethod
    def create(cls, target_file: Path) -> "MultipartUploadHandler":
        if not target_file.is_file():
            raise FileExistsError(f'{target_file} does not exist')

        if (target_file.parent / f"{target_file.stem}.upload.json").is_file():
            """ If resume file exists load this instead of recreating it """
            with cls.resume_file(target_file).open() as fp:
                return cls.parse_obj(json.load(fp))

        file_hash = md5sum(target_file)
        manifest = cls(file=target_file, filehash=file_hash, index=[])

        # split file & create upload index
        files_manifest, output_dir = split_archive(target_file)
        manifest.index = files_manifest
        manifest.output_dir = output_dir

        # save to disk to allow resume
        manifest.save()
        return manifest


    # todo should upload_next be an iterable and work with resume ?


class SinglePartUpload(BaseModel):
    file: Path
    filehash: str

    # todo: write section for single part
