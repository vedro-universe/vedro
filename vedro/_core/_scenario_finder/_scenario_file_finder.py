import os
from pathlib import Path
from typing import AsyncGenerator, Optional

from ._file_filters import FileFilter
from ._scenario_finder import ScenarioFinder

__all__ = ("ScenarioFileFinder",)


class ScenarioFileFinder(ScenarioFinder):
    def __init__(self, file_filter: Optional[FileFilter] = None,
                 dir_filter: Optional[FileFilter] = None) -> None:
        self._file_filter = file_filter
        self._dir_filter = dir_filter

    async def find(self, root: Path) -> AsyncGenerator[Path, None]:
        for path, dirs, files in os.walk(root):
            for dirname in dirs:
                dir_path = Path(os.path.join(path, dirname))
                if self._dir_filter and self._dir_filter.filter(dir_path):
                    dirs.remove(dirname)
            for filename in files:
                file_path = Path(os.path.join(path, filename))
                if self._file_filter and self._file_filter.filter(file_path):
                    continue
                yield file_path
