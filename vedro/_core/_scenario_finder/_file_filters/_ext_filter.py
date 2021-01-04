from pathlib import Path
from typing import List, Optional

from ._file_filter import FileFilter

__all__ = ("ExtFilter",)


class ExtFilter(FileFilter):
    def __init__(self, *,
                 only: Optional[List[str]] = None,
                 ignore: Optional[List[str]] = None) -> None:
        self._only = only or None
        self._ignore = ignore or None
        if (self._only is not None) and (self._ignore is not None):
            raise ValueError("Use 'only' or 'ignore' (not both)")

    def filter(self, path: Path) -> bool:
        if self._only:
            for suffix in self._only:
                if path.name.endswith(suffix):
                    return False
            return True
        if self._ignore:
            for suffix in self._ignore:
                if path.name.endswith(suffix):
                    return True
            return False
        return False
