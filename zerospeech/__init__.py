from importlib.metadata import version, PackageNotFoundError
from .startup import init

# initialise environment
init()


try:
    __version__ = version("zerospeech-benchmark")
except PackageNotFoundError:
    # package is not installed
    __version__ = None
