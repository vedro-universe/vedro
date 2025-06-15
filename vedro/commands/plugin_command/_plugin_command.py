from dataclasses import dataclass
from typing import Callable, List, Type, Union

from rich.console import Console
from rich.status import Status
from rich.table import Table

from vedro import Config

from .._cmd_arg_parser import CommandArgumentParser
from .._command import Command
from ._fetch_plugins import fetch_top_plugins
from ._get_plugin_info import get_plugin_info
from ._install_plugin import install_plugin
from .plugin_manager import PluginManager

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
        self._plugin_manager = PluginManager(config.path)

    async def run(self) -> None:
        subparsers = self._arg_parser.add_subparsers(dest="subparser")

        subparsers.add_parser("list", help="Show installed plugins")
        subparsers.add_parser("top", help="Show popular plugins")

        install_subparser = subparsers.add_parser("install", help="Install plugin")
        install_subparser.add_argument("packages", nargs="+", help="Package name(s)")
        install_subparser.add_argument("--pip-args", default="", help="Additional pip arguments")

        enable_subparser = subparsers.add_parser("enable", help="Enable plugin")
        enable_subparser.add_argument("plugin", help="Plugin name")

        disable_subparser = subparsers.add_parser("disable", help="Disable plugin")
        disable_subparser.add_argument("plugin", help="Plugin name")

        args = self._arg_parser.parse_args()
        if args.subparser == "top":
            await self._show_top_plugins()
        elif args.subparser == "list":
            await self._show_installed_plugins()
        elif args.subparser == "install":
            await self._install_packages(args.packages, args.pip_args)
        elif args.subparser == "enable":
            await self._enable_plugin(args.plugin)
        elif args.subparser == "disable":
            await self._disable_plugin(args.plugin)
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

    async def _install_packages(self, packages: List[str], pip_args: str) -> None:
        for package in packages:
            await self._install_package(package, pip_args)

    async def _install_package(self, package: str, pip_args: str) -> None:
        message = f"Installing '{package}'..."
        stdout, stderr = [], []

        def on_stdout(line: str, st: Status) -> None:
            stdout.append(line)
            last_line = "".join(stdout[-1:])
            st.update(f"{message}\n[grey50]{last_line}[/]")

        def on_stderr(line: str, st: Status) -> None:
            stderr.append(line)
            last_line = "".join(stderr[-1:])
            st.update(f"{message}\n[yellow]{last_line}[/]")

        with self._console.status(message) as status:
            return_code = await install_plugin(
                package=package,
                pip_args=pip_args,
                on_stdout=lambda line: on_stdout(line, status),
                on_stderr=lambda line: on_stderr(line, status),
            )

        if return_code == 0:
            enabled = await self._plugin_manager.enable(package)
            self._console.print(f"✔ Successfully installed '{package}'", style="green")
            if len(enabled) == 0:
                self._console.print(f"✗ Failed to enable '{package}'", style="red")
        else:
            self._console.print(f"✗ Failed to install '{package}'", style="red")
            self._console.print("".join(stdout), style="grey50", end="")
            self._console.print("".join(stderr), style="yellow", end="")

    async def _enable_plugin(self, plugin_name: str) -> None:
        enabled = await self._plugin_manager.enable(plugin_name)
        if len(enabled) == 0:
            self._console.print(f"✗ Plugin '{plugin_name}' not found", style="red")
            if discovered := await self._discover_core_plugin(plugin_name):
                self._console.print(f"? Did you mean '{discovered}'?", style="yellow")
        else:
            self._console.print(f"✔ Plugin '{plugin_name}' enabled", style="green")

    async def _disable_plugin(self, plugin_name: str) -> None:
        disabled = await self._plugin_manager.disable(plugin_name)
        if len(disabled) == 0:
            self._console.print(f"✗ Plugin '{plugin_name}' not found", style="red")
            if discovered := await self._discover_core_plugin(plugin_name):
                self._console.print(f"? Did you mean '{discovered}'?", style="yellow")
        else:
            self._console.print(f"✔ Plugin '{plugin_name}' disabled", style="green")

    async def _discover_core_plugin(self, plugin_name: str) -> Union[str, None]:
        discovered = await self._plugin_manager.discover(f"vedro.plugins.{plugin_name}")
        if discovered:
            return discovered[0][0]
        return None

    async def _show_installed_plugins(self) -> None:
        table = Table(expand=True, border_style="grey50")
        for column in ("Name", "Package", "Description", "Version", "Enabled"):
            table.add_column(column)

        for plugin_config in self._config.Plugins.values():
            plugin_info = get_plugin_info(plugin_config)

            color = "blue" if plugin_config.enabled else "grey70"
            enabled = "yes" if plugin_config.enabled else "no"
            table.add_row(plugin_info.name, plugin_info.package, plugin_info.summary,
                          plugin_info.version, enabled, style=color)

        self._console.print(table)
