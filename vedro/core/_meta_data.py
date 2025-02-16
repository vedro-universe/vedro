from types import MappingProxyType
from typing import Any, Dict, ItemsView

from niltype import Nil, Nilable

__all__ = ("MetaData",)


class MetaData:
    """
    Represents a container for storing metadata as key-value pairs.

    This class provides methods to check for the existence of keys, retrieve values,
    and iterate over the metadata items. The data is stored internally as a dictionary.
    """

    def __init__(self) -> None:
        """
        Initialize the MetaData instance.
        """
        self.__data: Dict[str, Any] = {}

    def has(self, key: str) -> bool:
        """
        Check if a key exists in the metadata.

        :param key: The key to check for existence.
        :return: True if the key exists, False otherwise.
        """
        return key in self.__data

    def get(self, key: str) -> Nilable[Any]:
        """
        Retrieve the value associated with a key in the metadata.

        :param key: The key whose value needs to be retrieved.
        :return: The value associated with the key, or Nil if the key does not exist.
        """
        return self.__data.get(key, Nil)

    def items(self) -> ItemsView[str, Any]:
        """
        Get an immutable view of the metadata items.

        :return: An ItemsView containing the key-value pairs in the metadata.
        """
        return MappingProxyType(self.__data).items()

    # Do not use this method directly
    # Use vedro.core.set_scenario_meta instead
    def _set(self, key: str, value: Any) -> None:
        """
        Set a key-value pair in the metadata.

        :param key: The key to set in the metadata.
        :param value: The value to associate with the key.
        """
        self.__data[key] = value

    def __repr__(self) -> str:
        """
        Return a string representation of the MetaData instance.

        :return: A string representing the MetaData instance and its contents.
        """
        return f"MetaData({self.__data})"
