from pathlib import Path
from typing import Type

from vedro import Config
from vedro.core import Dispatcher, Plugin
from vedro.events import (
    ArgParsedEvent,
    ArgParseEvent,
    CleanupEvent,
    ConfigLoadedEvent,
    StartupEvent,
)

from .._cmd_arg_parser import CommandArgumentParser
from .._command import Command

__all__ = ("RunCommand",)


class RunCommand(Command):
    def __init__(self, config: Type[Config], arg_parser: CommandArgumentParser) -> None:
        super().__init__(config, arg_parser)

    async def _register_plugins(self, dispatcher: Dispatcher) -> None:
        for _, section in self._config.Plugins.items():
            assert issubclass(section.plugin, Plugin)
            assert section.plugin != Plugin
            if section.enabled:
                plugin = section.plugin(config=section)
                dispatcher.register(plugin)

    async def _parse_args(self, dispatcher: Dispatcher) -> None:
        # https://github.com/python/cpython/issues/95073
        self._arg_parser.remove_help_action()
        await dispatcher.fire(ArgParseEvent(self._arg_parser))
        self._arg_parser.add_help_action()

        args = self._arg_parser.parse_args()
        await dispatcher.fire(ArgParsedEvent(args))

    async def run(self) -> None:
        dispatcher = self._config.Registry.Dispatcher()
        await self._register_plugins(dispatcher)

        await dispatcher.fire(ConfigLoadedEvent(self._config.Runtime.path, self._config))

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
        report = await runner.run(scheduler)

        await dispatcher.fire(CleanupEvent(report))
