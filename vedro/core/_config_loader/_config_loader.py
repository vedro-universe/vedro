from abc import ABC, abstractmethod
from pathlib import Path

from ._config_type import ConfigType

__all__ = ("ConfigLoader",)


class ConfigLoader(ABC):
    """
    Abstract base class for configuration loaders.

    Provides a framework for implementing custom configuration loading logic. Subclasses must
    implement the `load` method to define how configuration is loaded from a given path.
    """

    def __init__(self, default_config: ConfigType) -> None:
        """
        Initialize the ConfigLoader with a default configuration.

        :param default_config: The default configuration to use if no specific configuration
        is found.
        """
        self._default_config = default_config

    @abstractmethod
    async def load(self, path: Path) -> ConfigType:
        """
        Load a configuration from a given path.

        This method must be overridden by subclasses.

        :param path: The path to the configuration file.
        :return: The loaded configuration.
        """
        pass
