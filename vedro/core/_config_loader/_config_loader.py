from abc import ABC, abstractmethod
from pathlib import Path

from ._config_type import ConfigType

__all__ = ("ConfigLoader",)


class ConfigLoader(ABC):
    def __init__(self, default_config: ConfigType) -> None:
        self._default_config = default_config

    @abstractmethod
    async def load(self, path: Path) -> ConfigType:
        raise NotImplementedError()
