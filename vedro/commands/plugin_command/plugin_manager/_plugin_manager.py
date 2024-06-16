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
        return await self.toggle(plugin_name, enabled=True)

    async def disable(self, plugin_name: str) -> List[Tuple[str, str]]:
        return await self.toggle(plugin_name, enabled=False)

    async def toggle(self, plugin_name: str, *, enabled: bool) -> List[Tuple[str, str]]:
        plugins = self._get_plugins(plugin_name)
        for plugin_package, plugin_name in plugins:
            await self._config_updater.update(plugin_package, plugin_name, enabled=enabled)
        return plugins

    async def discover(self, plugin_name: str) -> List[Tuple[str, str]]:
        return self._get_plugins(plugin_name)

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
