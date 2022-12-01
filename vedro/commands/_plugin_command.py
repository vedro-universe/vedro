import sys

if sys.version_info >= (3, 8):
    from importlib.metadata import PackageNotFoundError, metadata
else:
    def metadata(name: str) -> None:
        raise PackageNotFoundError(name)
    PackageNotFoundError = Exception

from dataclasses import dataclass
from typing import Callable, Type

from rich.console import Console
from rich.table import Table

import vedro
from vedro import Config
from vedro.core import PluginConfig

from ._cmd_arg_parser import CommandArgumentParser
from ._command import Command

__all__ = ("PluginCommand", "PluginInfo",)


def make_console() -> Console:
    return Console(highlight=False, force_terminal=True, markup=False, soft_wrap=True)


@dataclass
class PluginInfo:
    name: str
    enabled: bool
    package: str = "Unknown"
    version: str = "Unknown"
    summary: str = "Unknown"


class PluginCommand(Command):
    def __init__(self, config: Type[Config], arg_parser: CommandArgumentParser, *,
                 console_factory: Callable[[], Console] = make_console) -> None:
        super().__init__(config, arg_parser)
        self._console = console_factory()

    def _get_plugin_info(self, plugin_config: PluginConfig) -> PluginInfo:
        plugin_name = getattr(plugin_config, "__name__", "Plugin")
        plugin_info = PluginInfo(plugin_name, plugin_config.enabled)

        plugin = plugin_config.plugin
        module = plugin.__module__
        package = module.split(".")[0]

        # core plugin
        if package == "vedro":
            plugin_info.package = ".".join(module.split(".")[:-1])
            plugin_info.version = vedro.__version__
            plugin_info.summary = "Core plugin"
            return plugin_info

        try:
            meta = metadata(package)
        except PackageNotFoundError:
            return plugin_info

        plugin_info.version = meta.get("Version", "Unknown")
        plugin_info.summary = meta.get("Summary", "Unknown")
        plugin_info.package = package
        return plugin_info

    async def run(self) -> None:
        table = Table(expand=True, border_style="grey50")

        for column in ("Name", "Package", "Description", "Version", "Enabled"):
            table.add_column(column)

        for plugin_config in self._config.Plugins.values():
            plugin_info = self._get_plugin_info(plugin_config)

            color = "blue" if plugin_config.enabled else "grey70"
            table.add_row(plugin_info.name, plugin_info.package, plugin_info.summary,
                          plugin_info.version, str(plugin_info.enabled), style=color)

        self._console.print(table)
