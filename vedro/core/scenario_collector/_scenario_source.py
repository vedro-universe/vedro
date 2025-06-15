from asyncio import Lock
from pathlib import Path
from types import ModuleType
from typing import Any, Union

from ..module_loader import ModuleLoader

__all__ = ("ScenarioSource",)


class ScenarioSource:
    """
    Represents the source of a scenario including its file path, project directory,
    and module loader.

    This class provides utilities to access the module and content associated with a scenario
    file while ensuring thread-safe lazy loading.
    """

    def __init__(self, path: Path, project_dir: Path, module_loader: ModuleLoader) -> None:
        """
        Initialize a ScenarioSource instance.

        :param path: The absolute or relative path to the scenario file.
        :param project_dir: The root directory of the project.
        :param module_loader: The module loader used to load the scenario module.
        """
        self._project_dir = project_dir if project_dir.is_absolute() else project_dir.absolute()
        self._path = path if path.is_absolute() else self._project_dir / path
        self._module_loader = module_loader
        self._module: Union[ModuleType, None] = None
        self._content: Union[str, None] = None
        self._lock = Lock()

    @property
    def path(self) -> Path:
        """
        Get the full path to the scenario file.

        :return: The full path as a Path object.
        """
        return self._path

    @property
    def rel_path(self) -> Path:
        """
        Get the scenario file path relative to the project directory.

        :return: A relative path to the scenario file.
        """
        return self._path.relative_to(self._project_dir)

    @property
    def project_dir(self) -> Path:
        """
        Get the root directory of the project.

        :return: The project directory as a Path object.
        """
        return self._project_dir

    async def get_module(self) -> ModuleType:
        """
        Load and return the module corresponding to the scenario file.

        The module is cached after the first load and protected by an asynchronous lock.

        :return: The loaded module object.
        :raises ModuleNotFoundError: If the module cannot be found or loaded.
        """
        async with self._lock:
            if self._module is None:
                self._module = await self._module_loader.load(self.rel_path)
        return self._module

    async def get_content(self) -> str:
        """
        Read and return the content of the scenario file.

        The content is cached after the first read and protected by an asynchronous lock.

        :return: The scenario file content as a string.
        """
        async with self._lock:
            if self._content is None:
                self._content = self._path.read_text()
        return self._content

    def __eq__(self, other: Any) -> bool:
        """
        Compare this ScenarioSource with another for equality.

        Two ScenarioSource instances are considered equal if their paths, project directories,
        and module loaders are equal.

        :param other: The object to compare against.
        :return: True if both instances are equivalent, False otherwise.
        """
        if not isinstance(other, ScenarioSource):
            return False
        return (
            self._path == other._path and
            self._project_dir == other._project_dir and
            self._module_loader == other._module_loader
        )

    def __repr__(self) -> str:
        """
        Return the string representation of the ScenarioSource.

        :return: A string that includes the relative path, project directory, and module loader.
        """
        return (
            f"ScenarioSource<path={self.rel_path!r}, project_dir={self._project_dir!r}), "
            f"module_loader={self._module_loader!r}>"
        )
