from inspect import isclass
from pathlib import Path
from typing import Any, Optional, cast

from .._module_loader import ModuleFileLoader, ModuleLoader
from ._config_loader import ConfigLoader
from ._config_type import Config, ConfigType

__all__ = ("ConfigFileLoader",)


class ConfigFileLoader(ConfigLoader):
    def __init__(self, default_config: ConfigType, *,
                 module_loader: Optional[ModuleLoader] = None) -> None:
        super().__init__(default_config)
        self._module_loader = module_loader or ModuleFileLoader()

    async def load(self, path: Path) -> ConfigType:
        if not path.exists():
            return self._default_config
        config = await self._get_config_class(path)

        # backward compatibility
        config.__frozen__ = False
        config.path = path
        config.__frozen__ = True

        return cast(ConfigType, config)

    async def _get_config_class(self, path: Path) -> ConfigType:
        module = await self._module_loader.load(path)

        for name in module.__dict__:
            if name.startswith("_"):
                continue
            val = getattr(module, name)
            if self._is_vedro_config(val, path):
                return cast(ConfigType, val)

        return self._default_config

    def _is_vedro_config(self, val: Any, path: Path) -> bool:
        # Non-class values cannot be Vedro config
        if not isclass(val):
            return False

        # Exclude the foundational 'Config' class as it's not a user-defined config class
        if val == Config:
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
