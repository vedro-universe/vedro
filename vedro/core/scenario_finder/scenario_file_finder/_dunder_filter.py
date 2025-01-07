from pathlib import Path

from ._file_filter import FileFilter

__all__ = ("DunderFilter",)


class DunderFilter(FileFilter):
    """
    Filters files or directories with names that start and end with double underscores.

    This filter matches paths like "__init__.py" or "__cache__".
    """

    def filter(self, path: Path) -> bool:
        """
        Check if the given path matches the dunder naming convention.

        :param path: The file or directory path to evaluate.
        :return: True if the name starts and ends with double underscores, otherwise False.
        """
        p = path
        while p.suffix != "":
            p = p.with_suffix("")
        stem = p.stem
        return stem.startswith("__") and stem.endswith("__")
