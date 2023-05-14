import re
from contextlib import redirect_stderr, redirect_stdout
from importlib import import_module
from inspect import isclass
from io import StringIO
from pathlib import Path
from types import ModuleType
from typing import List, Tuple, Union

from vedro.core import PluginConfig

from ._config_updater import ConfigUpdater

__all__ = ("PluginManager",)


class PluginManager:
    def __init__(self, config_path: Path) -> None:
        self._config_path = config_path
        self._config_updater = ConfigUpdater(config_path)

    async def enable(self, plugin_name: str) -> List[Tuple[str, str]]:
        return await self.toogle(plugin_name, enabled=True)

    async def disable(self, plugin_name: str) -> List[Tuple[str, str]]:
        return await self.toogle(plugin_name, enabled=False)

    async def toogle(self, plugin_name: str, *, enabled: bool) -> List[Tuple[str, str]]:
        ext_package = plugin_name.replace("-", "_")
        core_package = f"vedro.plugins.{self._to_snake_case(plugin_name)}"
        plugins = self._get_plugins(ext_package) or self._get_plugins(core_package)
        for plugin_package, plugin_name in plugins:
            await self._config_updater.update(plugin_package, plugin_name, enabled=enabled)
        return plugins

    def _to_snake_case(self, name: str) -> str:
        name = re.sub("(.)([A-Z][a-z]+)", r"1_\2", name)
        return re.sub("([a-z0-9])([A-Z])", r"1_\2", name).lower()

    def _get_plugins(self, plugin_package: str) -> List[Tuple[str, str]]:
        plugins: List[Tuple[str, str]] = []

        plugin_package = plugin_package.replace("-", "_")
        module = self._import_module(plugin_package)
        if module is None:
            return plugins

        for key, val in module.__dict__.items():
            if not key.startswith("_") and isclass(val) and issubclass(val, PluginConfig):
                plugins.append((plugin_package, key))
        return plugins

    def _import_module(self, module_name: str) -> Union[ModuleType, None]:
        with StringIO() as buf:
            with redirect_stdout(buf), redirect_stderr(buf):
                try:
                    return import_module(module_name)
                except ImportError:
                    return None
