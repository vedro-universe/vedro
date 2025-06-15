from pathlib import Path
from typing import List, Optional

from ._file_filter import FileFilter

__all__ = ("ExtFilter",)


class ExtFilter(FileFilter):
    """
    Filters files based on their extensions.

    This filter allows inclusion or exclusion of files based on their extensions.
    """

    def __init__(self, *,
                 only: Optional[List[str]] = None,
                 ignore: Optional[List[str]] = None) -> None:
        """
        Initialize the ExtFilter with inclusion or exclusion criteria.

        :param only: A list of extensions to include (e.g., ['.py', '.txt']).
                     If provided, only files with these extensions will pass.
        :param ignore: A list of extensions to exclude (e.g., ['.log', '.tmp']).
                       If provided, files with these extensions will not pass.
        :raises ValueError: If both 'only' and 'ignore' are specified simultaneously.
        """
        self._only = only or None
        self._ignore = ignore or None
        if (self._only is not None) and (self._ignore is not None):
            raise ValueError("Use 'only' or 'ignore' (not both)")

    def filter(self, path: Path) -> bool:
        """
        Check if the given path passes the extension filter.

        :param path: The file path to evaluate.
        :return: False if the file passes the filter criteria, otherwise True.
        """
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
