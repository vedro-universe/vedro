from pathlib import Path
from typing import Callable

from ..._plugin import Plugin
from ._local_storage import LocalStorage

LocalStorageFactory = Callable[[Plugin], LocalStorage]


def create_local_storage(plugin: Plugin) -> LocalStorage:
    """
    Create a new LocalStorage instance for the given plugin.

    :param plugin: The Plugin instance for which to create a LocalStorage.
    :return: The newly created LocalStorage instance.
    :raises TypeError: If the input is not a Plugin instance.
    """
    if not isinstance(plugin, Plugin):
        raise TypeError(f"Expected Plugin instance, but got {type(plugin)}")
    return LocalStorage(plugin, Path(".vedro/local_storage"))


__all__ = ("create_local_storage", "LocalStorageFactory", "LocalStorage",)
