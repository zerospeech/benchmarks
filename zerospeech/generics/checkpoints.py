from typing import ClassVar, Type

from zerospeech.misc import download_extract_archive
from zerospeech.out import console
from zerospeech.settings import get_settings
from .repository import DownloadableItem, RepoItemDir, RepositoryItemType

st = get_settings()


class CheckPointItem(DownloadableItem):
    key_name: ClassVar[RepositoryItemType] = "checkpoints"

    def pull(self, *, verify: bool = True, quiet: bool = False, show_progress: bool = False):
        md5_hash = ""
        if verify:
            md5_hash = self.origin.md5sum

        # download & extract archive
        download_extract_archive(self.origin.zip_url, self.location, int(self.origin.total_size),
                                 filename=self.name, md5sum_hash=md5_hash, quiet=quiet, show_progress=show_progress)
        if not quiet:
            console.print(f"[green]Checkpoint set {self.name} installed successfully !!")


class CheckpointDir(RepoItemDir):
    """ Checkpoint Directory Management """
    item_type: ClassVar[Type[DownloadableItem]] = CheckPointItem

    @classmethod
    def load(cls):
        return cls(root_dir=st.checkpoint_path)
