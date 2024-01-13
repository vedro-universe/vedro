from pathlib import Path

from ._file_filter import FileFilter

__all__ = ("DunderFilter",)


class DunderFilter(FileFilter):
    def filter(self, path: Path) -> bool:
        p = path
        while p.suffix != "":
            p = p.with_suffix("")
        stem = p.stem
        return stem.startswith("__") and stem.endswith("__")
