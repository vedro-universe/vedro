import os
import sys
from argparse import ArgumentDefaultsHelpFormatter, ArgumentParser
from pathlib import Path
from typing import List, Optional

from .._events import ArgParsedEvent, ArgParseEvent, CleanupEvent, StartupEvent
from ..plugins import Plugin
from ._dispatcher import Dispatcher
from ._runner import Runner
from ._scenario_discoverer import ScenarioDiscoverer

__all__ = ("Lifecycle",)


class Lifecycle:
    def __init__(self, dispatcher: Dispatcher,
                 discoverer: ScenarioDiscoverer,
                 plugins: Optional[List[Plugin]] = None) -> None:
        self._dispatcher = dispatcher
        self._discoverer = discoverer
        self._plugins = plugins if (plugins is not None) else []
        for plugin in self._plugins:
            self._dispatcher.register(plugin)

    async def start(self) -> None:
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

        runner = Runner(self._dispatcher)
        report = await runner.run(scenarios)

        await self._dispatcher.fire(CleanupEvent(report))
