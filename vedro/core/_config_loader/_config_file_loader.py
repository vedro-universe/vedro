from pathlib import Path
from typing import Optional

from .._module_loader import ModuleFileLoader, ModuleLoader
from ._config_loader import ConfigLoader
from ._config_type import Config, ConfigType

__all__ = ("ConfigFileLoader",)


class ConfigFileLoader(ConfigLoader):
    def __init__(self, default_config: ConfigType,
                 module_loader: Optional[ModuleLoader] = None) -> None:
        super().__init__(default_config)
        self._module_loader = module_loader or ModuleFileLoader()

    async def load(self, path: Path) -> ConfigType:
        if not path.exists():
            return self._default_config
        module = await self._module_loader.load(path)

        config = getattr(module, "Config", self._default_config)
        assert issubclass(config, Config)

        return config
