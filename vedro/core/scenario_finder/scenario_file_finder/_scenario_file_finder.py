import os
from pathlib import Path
from typing import AsyncGenerator, Optional

from .._scenario_finder import ScenarioFinder
from ._file_filter import FileFilter

__all__ = ("ScenarioFileFinder",)


class ScenarioFileFinder(ScenarioFinder):
    """
    A class for finding scenario files within a directory structure.

    This class extends ScenarioFinder and provides functionality to traverse a directory
    and identify files that match certain criteria defined by file and directory filters.
    """

    def __init__(self, file_filter: Optional[FileFilter] = None,
                 dir_filter: Optional[FileFilter] = None) -> None:
        """
        Initialize the ScenarioFileFinder with optional file and directory filters.

        :param file_filter: An optional FileFilter to apply to each file found. If provided,
                            only files that pass the filter will be included.
        :param dir_filter: An optional FileFilter to apply to each directory found. If provided,
                           directories that do not pass the filter will be skipped, along with
                           their contents.
        """
        self._file_filter = file_filter
        self._dir_filter = dir_filter

    async def find(self, root: Path) -> AsyncGenerator[Path, None]:
        """
        Find and yield scenario file paths starting from the given root directory.

        This method traverses the directory tree starting from the specified root. It applies
        file and directory filters (if provided) to identify relevant scenario files.

        :param root: The root directory path to start the search from.
        :yield: Paths to scenario files that match the given criteria.
        """
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
