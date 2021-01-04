from pathlib import Path
from typing import List

from ._file_filter import FileFilter

__all__ = ("AnyFilter",)


class AnyFilter(FileFilter):
    def __init__(self, filters: List[FileFilter]) -> None:
        self._filters = filters

    def filter(self, path: Path) -> bool:
        for filter_ in self._filters:
            if filter_.filter(path):
                return True
        return False
