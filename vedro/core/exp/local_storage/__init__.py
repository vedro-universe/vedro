from typing import Callable

from ..._plugin import Plugin
from ._local_storage import LocalStorage

LocalStorageFactory = Callable[[Plugin], LocalStorage]


def create_local_storage(plugin: Plugin) -> LocalStorage:
    """
    Create and return a new LocalStorage instance for a given plugin.

    :param plugin: The Plugin instance for which the LocalStorage is to be created.
    :return: A LocalStorage instance associated with the given plugin.
    :raises TypeError: If the provided plugin is not an instance of Plugin.
    """
    if not isinstance(plugin, Plugin):
        raise TypeError(f"Expected Plugin instance, but got {type(plugin)}")
    return LocalStorage(plugin)


__all__ = ("create_local_storage", "LocalStorageFactory", "LocalStorage",)
