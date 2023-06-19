""" File containing rich printing utilities """
import contextlib
from types import TracebackType
from typing import IO, Type, AnyStr, Iterator, Iterable, Union, Optional, List, Generator

from rich.console import Console
from rich.progress import (
    Progress, TextColumn, BarColumn, TaskProgressColumn, TimeElapsedColumn,
    FileSizeColumn, TotalFileSizeColumn, SpinnerColumn
)
from rich.table import Column


class DevNull(IO[str]):
    """ Class emulating /dev/null functionality """

    def close(self) -> None:
        """ /dev/null no interaction needed """
        pass

    def fileno(self) -> int:
        """ /dev/null no interaction needed """
        pass

    def flush(self) -> None:
        """ /dev/null no interaction needed """
        pass

    def isatty(self) -> bool:
        """ /dev/null no interaction needed """
        pass

    def read(self, __n: int = ...) -> AnyStr:
        """ /dev/null no interaction needed """
        pass

    def readable(self) -> bool:
        """ /dev/null no interaction needed """
        pass

    def readline(self, __limit: int = ...) -> AnyStr:
        """ /dev/null no interaction needed """
        pass

    def readlines(self, __hint: int = ...) -> List[AnyStr]:
        """ /dev/null no interaction needed """
        pass

    def seek(self, __offset: int, __whence: int = ...) -> int:
        """ /dev/null no interaction needed """
        pass

    def seekable(self) -> bool:
        """ /dev/null no interaction needed """
        pass

    def tell(self) -> int:
        """ /dev/null no interaction needed """
        pass

    def truncate(self, __size: Union[int, None] = ...) -> int:
        """ /dev/null no interaction needed """
        pass

    def writable(self) -> bool:
        """ /dev/null no interaction needed """
        pass

    def writelines(self, __lines: Iterable[AnyStr]) -> None:
        """ /dev/null no interaction needed """
        pass

    def __next__(self) -> AnyStr:
        """ /dev/null no interaction needed """
        pass

    def __iter__(self) -> Iterator[AnyStr]:
        """ /dev/null no interaction needed """
        pass

    def __enter__(self) -> IO[AnyStr]:
        """ /dev/null no interaction needed """
        pass

    def __exit__(self, __t: Optional[Type[BaseException]], __value: Optional[BaseException],
                 __traceback: Optional[TracebackType]) -> Optional[bool]:
        """ /dev/null no interaction needed """
        pass

    def write(self, *_):
        """ /dev/null no interaction needed """
        pass


console = Console(log_time_format="[info]")
warning_console = Console(stderr=True, style="bold yellow", log_time_format="[warning]")
error_console = Console(stderr=True, style="bold red", log_time_format="[error]")
void_console = Console(file=DevNull())


@contextlib.contextmanager
def with_progress(show: bool = True, file_transfer: bool = False, spinner: bool = False) -> Generator[
    Progress, None, None]:
    if show:
        con = console
    else:
        con = void_console

    bar_items = [
        TextColumn("{task.description}", table_column=Column(ratio=1)),
        BarColumn(bar_width=None, table_column=Column(ratio=2))
    ]
    if file_transfer:
        bar_items.append(FileSizeColumn())
        bar_items.append(TotalFileSizeColumn())
    else:
        bar_items.append(TaskProgressColumn())

    if spinner:
        bar_items.append(SpinnerColumn())

    bar_items.append(TimeElapsedColumn())
    progress = Progress(*bar_items, console=con, expand=True, transient=True)

    with progress:
        yield progress
