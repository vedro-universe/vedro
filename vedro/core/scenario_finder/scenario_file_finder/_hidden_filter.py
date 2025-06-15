from pathlib import Path

from ._file_filter import FileFilter

__all__ = ("HiddenFilter",)


class HiddenFilter(FileFilter):
    """
    Filters hidden files and directories.

    This filter matches paths whose names start with a dot (e.g., ".hidden").
    """

    def filter(self, path: Path) -> bool:
        """
        Check if the given path is hidden.

        :param path: The file or directory path to evaluate.
        :return: True if the name starts with a dot, otherwise False.
        """
        return path.name.startswith(".")
