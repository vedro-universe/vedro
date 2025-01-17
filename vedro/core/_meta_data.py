from typing import Any, Dict, Optional

from niltype import Nil, Nilable

__all__ = ("MetaData",)


class MetaData:
    def __init__(self, data: Optional[Dict[str, Any]] = None) -> None:
        self.__data = data or {}

    def has(self, key: str) -> bool:
        return key in self.__data

    def get(self, key: str) -> Nilable[Any]:
        return self.__data.get(key, Nil)

    # Do not use this method directly. Use set_scenario_meta() instead.
    def _set(self, key: str, value: Any) -> None:
        self.__data[key] = value
