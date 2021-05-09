from pathlib import Path

from ._file_filter import FileFilter

__all__ = ("HiddenFilter",)


class HiddenFilter(FileFilter):
    def filter(self, path: Path) -> bool:
        return path.name.startswith(".")
