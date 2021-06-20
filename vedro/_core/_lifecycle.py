import os
import sys
from argparse import ArgumentDefaultsHelpFormatter, ArgumentParser
from asyncio import CancelledError
from pathlib import Path
from typing import List

from .._events import ArgParsedEvent, ArgParseEvent, CleanupEvent, StartupEvent
from ..plugins import Plugin
from ._dispatcher import Dispatcher
from ._report import Report
from ._runner import Runner
from ._scenario_discoverer import ScenarioDiscoverer

__all__ = ("Lifecycle",)


class Lifecycle:
    def __init__(self, dispatcher: Dispatcher, discoverer: ScenarioDiscoverer) -> None:
        self._dispatcher = dispatcher
        self._discoverer = discoverer
        self._plugins: List[Plugin] = []

    def register_plugins(self, plugins: List[Plugin]) -> None:
        for plugin in plugins:
            self._dispatcher.register(plugin)
            self._plugins.append(plugin)

    async def start(self) -> Report:
        os.chdir(os.path.dirname(os.path.join(os.getcwd(), sys.argv[0])))

        formatter = ArgumentDefaultsHelpFormatter
        arg_parser = ArgumentParser("vedro", formatter_class=formatter, add_help=False)
        await self._dispatcher.fire(ArgParseEvent(arg_parser))
        arg_parser.add_argument("-h", "--help",
                                action="help", help="show this help message and exit")
        args = arg_parser.parse_args()
        await self._dispatcher.fire(ArgParsedEvent(args))

        start_dir = os.path.relpath(Path("scenarios"))
        scenarios = await self._discoverer.discover(Path(start_dir))
        await self._dispatcher.fire(StartupEvent(scenarios))

        runner = Runner(self._dispatcher, (KeyboardInterrupt, SystemExit, CancelledError,))
        report = await runner.run(scenarios)

        await self._dispatcher.fire(CleanupEvent(report))

        return report

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self._dispatcher!r}, {self._discoverer!r})"
