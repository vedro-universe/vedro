from pathlib import Path
from typing import Callable

from ..._plugin import Plugin
from ._local_storage import LocalStorage

LocalStorageFactory = Callable[[Plugin, Path], LocalStorage]


def create_local_storage(plugin: Plugin, project_dir: Path) -> LocalStorage:
    """
    Create and return a new LocalStorage instance for a given plugin.

    :param plugin: The Plugin instance for which the LocalStorage is to be created.
    :param project_dir: The root directory of the project.
    :return: A LocalStorage instance associated with the given plugin.
    :raises TypeError: If the provided plugin is not an instance of Plugin.
    """
    if not isinstance(plugin, Plugin):
        raise TypeError(f"Expected Plugin instance, but got {type(plugin)}")
    return LocalStorage(plugin, project_dir)


__all__ = ("create_local_storage", "LocalStorageFactory", "LocalStorage",)
