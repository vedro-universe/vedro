import os
from argparse import ArgumentParser, HelpFormatter
from functools import partial
from pathlib import Path
from typing import List

from ..events import ArgParsedEvent, ArgParseEvent, CleanupEvent, StartupEvent
from ._dispatcher import Dispatcher
from ._plugin import Plugin
from ._report import Report
from ._runner import Runner
from ._scenario_discoverer import ScenarioDiscoverer

__all__ = ("Lifecycle",)


class Lifecycle:
    def __init__(self,
                 dispatcher: Dispatcher,
                 discoverer: ScenarioDiscoverer,
                 runner: Runner) -> None:
        self._dispatcher = dispatcher
        self._discoverer = discoverer
        self._runner = runner
        self._plugins: List[Plugin] = []

    def register_plugins(self, plugins: List[Plugin]) -> None:
        for plugin in plugins:
            self._dispatcher.register(plugin)
            self._plugins.append(plugin)

    async def start(self) -> Report:
        formatter = partial(HelpFormatter, max_help_position=30)
        arg_parser = ArgumentParser("vedro", formatter_class=formatter, add_help=False)

        await self._dispatcher.fire(ArgParseEvent(arg_parser))
        arg_parser.add_argument("-h", "--help",
                                action="help", help="Show this help message and exit")
        args = arg_parser.parse_args()
        await self._dispatcher.fire(ArgParsedEvent(args))

        start_dir = os.path.relpath(Path("scenarios"))
        scenarios = await self._discoverer.discover(Path(start_dir))
        await self._dispatcher.fire(StartupEvent(scenarios))

        report = await self._runner.run(scenarios)

        await self._dispatcher.fire(CleanupEvent(report))

        return report

    def __repr__(self) -> str:
        cls_name = self.__class__.__name__
        return f"{cls_name}({self._dispatcher!r}, {self._discoverer!r}, {self._runner!r})"
