import inspect
import os
import warnings
from argparse import Namespace
from pathlib import Path
from typing import Set, Type

from vedro import Config
from vedro.core import Dispatcher, MonotonicScenarioRunner, Plugin, PluginConfig
from vedro.events import (
    ArgParsedEvent,
    ArgParseEvent,
    CleanupEvent,
    ConfigLoadedEvent,
    StartupEvent,
)
from vedro.plugins.dry_runner import DryRunner

from .._cmd_arg_parser import CommandArgumentParser
from .._command import Command

__all__ = ("RunCommand",)


class RunCommand(Command):
    def __init__(self, config: Type[Config], arg_parser: CommandArgumentParser) -> None:
        """
        Initialize a new instance of the RunCommand class.

        :param config: Global configuration
        :param arg_parser: Argument parser for command-line options
        """
        super().__init__(config, arg_parser)

    def _validate_config(self) -> None:
        default_scenarios_dir = self._config.default_scenarios_dir
        if not isinstance(default_scenarios_dir, (Path, str)):
            raise TypeError(
                "Expected `default_scenarios_dir` to be a Path, "
                f"got {type(default_scenarios_dir)} ({default_scenarios_dir!r})"
            )

        scenarios_dir = Path(default_scenarios_dir).resolve()
        if not scenarios_dir.exists():
            raise FileNotFoundError(
                f"`default_scenarios_dir` ('{scenarios_dir}') does not exist"
            )

        if not scenarios_dir.is_dir():
            raise NotADirectoryError(
                f"`default_scenarios_dir` ('{scenarios_dir}') is not a directory"
            )

        try:
            scenarios_dir.relative_to(self._config.project_dir)
        except ValueError:
            raise ValueError(
                f"`default_scenarios_dir` ('{scenarios_dir}') must be inside project directory "
                f"('{self._config.project_dir}')"
            )

    async def _register_plugins(self, dispatcher: Dispatcher) -> None:
        """
        Register plugins with the dispatcher.

        :param dispatcher: Dispatcher to register plugins with
        """
        for _, section in self._config.Plugins.items():
            if not issubclass(section.plugin, Plugin) or (section.plugin is Plugin):
                raise TypeError(
                    f"Plugin {section.plugin} should be subclass of vedro.core.Plugin"
                )

            if self._config.validate_plugins_configs:
                self._validate_plugin_config(section)

            if section.enabled:
                plugin = section.plugin(config=section)
                dispatcher.register(plugin)

    def _validate_plugin_config(self, plugin_config: Type[PluginConfig]) -> None:
        """
        Validate plugin's configuration.

        :param plugin_config: Configuration of the plugin.
        """
        unknown_attrs = self._get_attrs(plugin_config) - self._get_parent_attrs(plugin_config)
        if unknown_attrs:
            attrs = ", ".join(unknown_attrs)
            raise AttributeError(
                f"{plugin_config.__name__} configuration contains unknown attributes: {attrs}"
            )

    def _get_attrs(self, cls: type) -> Set[str]:
        """
        Get the set of attributes for a class.

        :param cls: The class to get attributes for
        :return: The set of attribute names for the class
        """
        return set(vars(cls))

    def _get_parent_attrs(self, cls: type) -> Set[str]:
        """
        Recursively get attributes from parent classes.

        :param cls: The class to get parent attributes for
        :return: The set of attribute names for the parent classes
        """
        attrs = set()
        # `object` (the base for all classes) has no __bases__
        for base in cls.__bases__:
            attrs |= self._get_attrs(base)
            attrs |= self._get_parent_attrs(base)
        return attrs

    async def _parse_args(self, dispatcher: Dispatcher) -> Namespace:
        """
        Parse command-line arguments and fire corresponding dispatcher events.

        :param dispatcher: The dispatcher to fire events
        """

        # Avoid unrecognized arguments error
        help_message = ("Specify the root directory of the project, used as a reference point for "
                        "relative paths and file operations. "
                        "Defaults to the directory from which the command is executed.")
        self._arg_parser.add_argument("--project-dir", type=Path,
                                      default=self._config.project_dir,
                                      help=help_message)

        # https://github.com/python/cpython/issues/95073
        self._arg_parser.remove_help_action()
        await dispatcher.fire(ArgParseEvent(self._arg_parser))
        self._arg_parser.add_help_action()

        args = self._arg_parser.parse_args()
        await dispatcher.fire(ArgParsedEvent(args))

        return args

    async def run(self) -> None:
        """
        Execute the command, including plugin registration, event dispatching,
        and scenario execution.
        """
        self._validate_config()  # Must be before ConfigLoadedEvent

        dispatcher = self._config.Registry.Dispatcher()
        await self._register_plugins(dispatcher)

        await dispatcher.fire(ConfigLoadedEvent(self._config.path, self._config))

        args = await self._parse_args(dispatcher)
        start_dir = self._get_start_dir(args)

        discoverer = self._config.Registry.ScenarioDiscoverer()

        kwargs = {}
        # Backward compatibility (to be removed in v2):
        signature = inspect.signature(discoverer.discover)
        if "project_dir" in signature.parameters:
            kwargs["project_dir"] = self._config.project_dir

        try:
            scenarios = await discoverer.discover(start_dir, **kwargs)
        except SystemExit as e:
            raise Exception(f"SystemExit({e.code}) ⬆")

        scheduler = self._config.Registry.ScenarioScheduler(scenarios)
        await dispatcher.fire(StartupEvent(scheduler))

        runner = self._config.Registry.ScenarioRunner()
        if not isinstance(runner, (MonotonicScenarioRunner, DryRunner)):
            warnings.warn("Deprecated: custom runners will be removed in v2.0", DeprecationWarning)
        report = await runner.run(scheduler)

        await dispatcher.fire(CleanupEvent(report))

    def _get_start_dir(self, args: Namespace) -> Path:
        """
        Determine the starting directory for discovering scenarios.

        :param args: Parsed command-line arguments
        :return: The resolved starting directory
        """
        common_path = os.path.commonpath([self._normalize_path(x) for x in args.file_or_dir])
        start_dir = Path(common_path).resolve()
        if not start_dir.is_dir():
            start_dir = start_dir.parent

        try:
            start_dir.relative_to(self._config.project_dir)
        except ValueError:
            raise ValueError(
                f"The start directory '{start_dir}' must be inside the project directory "
                f"('{self._config.project_dir}')"
            )

        return start_dir

    def _normalize_path(self, file_or_dir: str) -> str:
        path = os.path.normpath(file_or_dir)
        if os.path.isabs(path):
            return path

        # Backward compatibility (to be removed in v2):
        # Only prepend "scenarios/" if:
        # 1) The default_scenarios_dir is exactly <project_dir>/scenarios
        # 2) The original path does not exist, but "scenarios/<path>" does
        scenarios_dir = Path(self._config.default_scenarios_dir).resolve()
        if scenarios_dir == self._config.project_dir / "scenarios":
            updated_path = os.path.join("scenarios/", path)
            if not os.path.exists(path) and os.path.exists(updated_path):
                return os.path.abspath(updated_path)

        return os.path.abspath(path)
