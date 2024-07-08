import argparse

from .generics import RepositoryIndex

repo = RepositoryIndex.load()


def datasets_info():
    for dt in repo.datasets:
        print(f"{dt.name} | {dt.total_size}B")

