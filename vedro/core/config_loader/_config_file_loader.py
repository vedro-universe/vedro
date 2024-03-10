from inspect import isclass
from pathlib import Path
from typing import Any, Optional, cast

from ..module_loader import ModuleFileLoader, ModuleLoader
from ._config_loader import ConfigLoader
from ._config_type import Config, ConfigType

__all__ = ("ConfigFileLoader",)


class ConfigFileLoader(ConfigLoader):
    """
    Configuration loader for loading configurations from files.

    Extends the `ConfigLoader` abstract base class, providing an implementation for loading
    configuration data from file paths.
    """

    def __init__(self, default_config: ConfigType, *,
                 module_loader: Optional[ModuleLoader] = None) -> None:
        """
        Initialize the ConfigFileLoader with a default configuration and an optional module loader.

        :param default_config: The default configuration to use if no specific configuration
        is found.
        :param module_loader: An optional module loader to use for loading configuration files.
        """
        super().__init__(default_config)
        self._module_loader = module_loader or ModuleFileLoader()

    async def load(self, path: Path) -> ConfigType:
        """
        Load a configuration from a file at the given path.

        :param path: The path to the configuration file.
        :return: The loaded configuration, or the default configuration if the file does not exist.
        """
        config = await self._get_config_class(path) if path.exists() else self._default_config

        # backward compatibility
        config.__frozen__ = False
        config.project_dir = path.parent.absolute()
        config.path = config.path.absolute() if config is self._default_config else path.absolute()
        config.__frozen__ = True

        return cast(ConfigType, config)

    async def _get_config_class(self, path: Path) -> ConfigType:
        """
        Get the configuration class from a file at the given path.

        :param path: The path to the file containing the configuration class.
        :return: The configuration class, or the default configuration if no valid class is found.
        """
        module = await self._module_loader.load(path)

        for name in module.__dict__:
            if name.startswith("_"):
                continue
            val = getattr(module, name)
            if self._is_vedro_config(val, path):
                return cast(ConfigType, val)

        return self._default_config

    def _is_vedro_config(self, val: Any, path: Path) -> bool:
        """
        Check whether a given value is a valid Vedro configuration class.

        :param val: The value to check.
        :param path: The path to the file containing the value.
        :return: True if the value is a valid Vedro configuration class, False otherwise.
        """
        if not isclass(val) or val == Config:
            return False

        is_config_subclass = issubclass(val, Config)
        cls_name = val.__name__
        is_named_config = cls_name == "Config"

        if is_config_subclass and is_named_config:
            return True
        elif is_config_subclass:
            raise ValueError(f"'{cls_name}' in '{path}' must be named 'Config'")
        elif is_named_config:
            raise TypeError(f"'Config' in '{path}' must inherit from 'vedro.Config'")
        else:
            return False
