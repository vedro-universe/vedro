import warnings
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

    async def _register_plugins(self, dispatcher: Dispatcher) -> None:
        """
        Register plugins with the dispatcher.

        :param dispatcher: Dispatcher to register plugins with
        """
        for _, section in self._config.Plugins.items():
            if not issubclass(section.plugin, Plugin) or (section.plugin is Plugin):
                raise TypeError(
                    f"Plugin {section.plugin} should be subclass of vedro.core.Plugin")

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
                f"{plugin_config.__name__} configuration contains unknown attributes: {attrs}")

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

    async def _parse_args(self, dispatcher: Dispatcher) -> None:
        """
        Parse command-line arguments and fire corresponding dispatcher events.

        :param dispatcher: The dispatcher to fire events
        """
        # https://github.com/python/cpython/issues/95073
        self._arg_parser.remove_help_action()
        await dispatcher.fire(ArgParseEvent(self._arg_parser))
        self._arg_parser.add_help_action()

        args = self._arg_parser.parse_args()
        await dispatcher.fire(ArgParsedEvent(args))

    async def run(self) -> None:
        """
        Execute the command, including plugin registration, event dispatching,
        and scenario execution.
        """
        dispatcher = self._config.Registry.Dispatcher()
        await self._register_plugins(dispatcher)

        await dispatcher.fire(ConfigLoadedEvent(self._config.path, self._config))

        await self._parse_args(dispatcher)

        start_dir = Path("scenarios")
        discoverer = self._config.Registry.ScenarioDiscoverer()
        try:
            scenarios = await discoverer.discover(start_dir)
        except SystemExit as e:
            raise Exception(f"SystemExit({e.code}) ⬆")

        scheduler = self._config.Registry.ScenarioScheduler(scenarios)
        await dispatcher.fire(StartupEvent(scheduler))

        runner = self._config.Registry.ScenarioRunner()
        if not isinstance(runner, (MonotonicScenarioRunner, DryRunner)):
            warnings.warn("Deprecated: custom runners will be removed in v2.0", DeprecationWarning)
        report = await runner.run(scheduler)

        await dispatcher.fire(CleanupEvent(report))
