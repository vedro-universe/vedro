from abc import ABC, abstractmethod
from pathlib import Path

__all__ = ("FileFilter",)


class FileFilter(ABC):
    """
    Abstract base class for file filters.

    This class provides a common interface for filters that determine whether a file
    or directory should be included or excluded based on custom logic.
    """

    @abstractmethod
    def filter(self, path: Path) -> bool:
        """
        Determine whether the given path passes the filter.

        :param path: The file or directory path to evaluate.
        :return: True if the path should be excluded, otherwise False.
        """
        pass
