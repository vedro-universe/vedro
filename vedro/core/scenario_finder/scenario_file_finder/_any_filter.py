from pathlib import Path
from typing import List

from ._file_filter import FileFilter

__all__ = ("AnyFilter",)


class AnyFilter(FileFilter):
    """
    Combines multiple filters using a logical OR operation.

    This filter passes a path if at least one of the provided filters passes the path.
    """

    def __init__(self, filters: List[FileFilter]) -> None:
        """
        Initialize the AnyFilter with a list of filters.

        :param filters: A list of FileFilter objects to combine.
        """
        self._filters = filters

    def filter(self, path: Path) -> bool:
        """
        Check if the given path passes any of the filters.

        :param path: The file or directory path to evaluate.
        :return: True if at least one filter passes the path, otherwise False.
        """
        for filter_ in self._filters:
            if filter_.filter(path):
                return True
        return False

    def __repr__(self) -> str:
        """
        Return a string representation of the filter.

        The representation includes the class name and the inner filters in creation order.

        :return: A string describing the filter and its composed filters.
        """
        inner = ", ".join(repr(f) for f in self._filters)
        return f"{self.__class__.__name__}([{inner}])"
