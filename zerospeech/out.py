""" File containing rich printing utilities """
import contextlib
from types import TracebackType
from typing import IO, Type, AnyStr, Iterator, Iterable, Union, Optional, List

from rich.console import Console
from rich.progress import (
    Progress, TextColumn, BarColumn, TaskProgressColumn, TimeElapsedColumn,
    FileSizeColumn, TotalFileSizeColumn, SpinnerColumn
)
from rich.table import Column


class DevNull(IO[str]):
    """ Class emulating /dev/null functionality """
    def close(self) -> None:
        pass

    def fileno(self) -> int:
        pass

    def flush(self) -> None:
        pass

    def isatty(self) -> bool:
        pass

    def read(self, __n: int = ...) -> AnyStr:
        pass

    def readable(self) -> bool:
        pass

    def readline(self, __limit: int = ...) -> AnyStr:
        pass

    def readlines(self, __hint: int = ...) -> List[AnyStr]:
        pass

    def seek(self, __offset: int, __whence: int = ...) -> int:
        pass

    def seekable(self) -> bool:
        pass

    def tell(self) -> int:
        pass

    def truncate(self, __size: Union[int, None] = ...) -> int:
        pass

    def writable(self) -> bool:
        pass

    def writelines(self, __lines: Iterable[AnyStr]) -> None:
        pass

    def __next__(self) -> AnyStr:
        pass

    def __iter__(self) -> Iterator[AnyStr]:
        pass

    def __enter__(self) -> IO[AnyStr]:
        pass

    def __exit__(self, __t: Optional[Type[BaseException]], __value: Optional[BaseException],
                 __traceback: Optional[TracebackType]) -> Optional[bool]:
        pass

    def write(self, *_):
        pass


console = Console(log_time_format="[info]")
warning_console = Console(stderr=True, style="bold yellow", log_time_format="[warning]")
error_console = Console(stderr=True, style="bold red", log_time_format="[error]")
void_console = Console(file=DevNull())


@contextlib.contextmanager
def with_progress(show: bool = True, file_transfer: bool = False, spinner: bool = False) -> Progress:
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
