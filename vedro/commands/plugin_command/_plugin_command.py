import sys
from typing import Dict

if sys.version_info >= (3, 8):
    from importlib.metadata import PackageNotFoundError, metadata
else:
    def metadata(name: str) -> Dict[str, str]:
        raise PackageNotFoundError(name)
    PackageNotFoundError = Exception

from dataclasses import dataclass
from typing import Callable, Type

from rich.console import Console
from rich.table import Table

import vedro
from vedro import Config
from vedro.core import PluginConfig

from .._cmd_arg_parser import CommandArgumentParser
from .._command import Command
from ._fetch_plugins import fetch_top_plugins
from ._install_plugin import install_plugin

__all__ = ("PluginCommand", "PluginInfo",)


def make_console() -> Console:
    return Console(highlight=False, force_terminal=True, markup=False, soft_wrap=True)


@dataclass
class PluginInfo:
    name: str
    enabled: bool
    package: str = "Unknown"
    version: str = "0.0.0"
    summary: str = "No data"
    is_default: bool = False


class PluginCommand(Command):
    def __init__(self, config: Type[Config], arg_parser: CommandArgumentParser, *,
                 console_factory: Callable[[], Console] = make_console) -> None:
        super().__init__(config, arg_parser)
        self._console = console_factory()

    def _get_plugin_info(self, plugin_config: Type[PluginConfig]) -> PluginInfo:
        plugin_name = getattr(plugin_config, "__name__", "Plugin")
        plugin_info = PluginInfo(plugin_name, plugin_config.enabled)

        plugin = plugin_config.plugin
        module = plugin.__module__
        package = module.split(".")[0]

        # plugin declared in vedro.cfg.py
        if module == self._config.__module__:
            return plugin_info

        # default plugin
        if package == "vedro":
            summary = plugin_config.description or "Core Plugin"
            plugin_info.package = ".".join(module.split(".")[:-1])
            plugin_info.version = vedro.__version__
            plugin_info.summary = summary
            plugin_info.is_default = True
            return plugin_info

        try:
            meta = metadata(package)
        except PackageNotFoundError:
            return plugin_info

        plugin_info.package = package
        if "Version" in meta:
            plugin_info.version = meta["Version"]
        if "Summary" in meta:
            plugin_info.summary = meta["Summary"]
        return plugin_info

    async def _show_installed_plugins(self) -> None:
        table = Table(expand=True, border_style="grey50")
        for column in ("Name", "Package", "Description", "Version", "Enabled"):
            table.add_column(column)

        for plugin_config in self._config.Plugins.values():
            plugin_info = self._get_plugin_info(plugin_config)

            color = "blue" if plugin_config.enabled else "grey70"
            table.add_row(plugin_info.name, plugin_info.package, plugin_info.summary,
                          plugin_info.version, str(plugin_info.enabled), style=color)

        self._console.print(table)

    async def run(self) -> None:
        subparsers = self._arg_parser.add_subparsers(dest="subparser")

        subparsers.add_parser("list", help="Show installed plugins")
        subparsers.add_parser("top", help="Show popular plugins")

        install_subparser = subparsers.add_parser("install", help="Install plugin")
        install_subparser.add_argument("package", help="Package name")
        install_subparser.add_argument("--pip-args", default="", help="Additional pip arguments")

        args = self._arg_parser.parse_args()
        if args.subparser == "top":
            await self._show_top_plugins()
        elif args.subparser == "list":
            await self._show_installed_plugins()
        elif args.subparser == "install":
            if sys.version_info < (3, 8):
                self._console.print("Python 3.8+ required for this command", style="red")
                return
            await self._install_plugin(args.package, args.pip_args)
        else:
            self._arg_parser.print_help()
            self._arg_parser.exit()

    async def _show_top_plugins(self) -> None:
        with self._console.status("Fetching plugins..."):
            try:
                plugins = await fetch_top_plugins(limit=10, timeout=10.0)
            except Exception as e:
                self._console.print(f"Failed to fetch popular plugins ({e})", style="red")
                return

        table = Table(expand=True, border_style="grey50")
        table.add_column("Package", overflow="fold", style="blue")
        table.add_column("Description", overflow="fold")
        table.add_column("URL", overflow="fold")
        table.add_column("Popularity", justify="right")

        for plugin in plugins:
            table.add_row(plugin["name"], plugin["description"],
                          plugin["url"], str(plugin["popularity"]))

        self._console.print(table)

    async def _install_plugin(self, package: str, pip_args: str) -> None:
        with self._console.status(f"Installing '{package}' package..."):
            await install_plugin(
                package=package,
                pip_args=pip_args,
                on_stdout=lambda x: self._console.print(x, style="grey50", end=""),
                on_stderr=lambda x: self._console.print(x, style="yellow", end=""),
            )
