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
        self._plugins = plugins if plugins else []
        for plugin in self._plugins:
            self._dispatcher.register(plugin)

    async def start(self) -> None:
        os.chdir(os.path.dirname(os.path.join(os.getcwd(), sys.argv[0])))

        arg_parser = ArgumentParser(formatter_class=ArgumentDefaultsHelpFormatter)
        await self._dispatcher.fire(ArgParseEvent(arg_parser))
        args = arg_parser.parse_args()
        await self._dispatcher.fire(ArgParsedEvent(args))

        start_dir = os.path.relpath(Path("scenarios"))
        scenarios = await self._discoverer.discover(Path(start_dir))
        await self._dispatcher.fire(StartupEvent(scenarios))

        runner = Runner(self._dispatcher)
        report = await runner.run(scenarios)

        await self._dispatcher.fire(CleanupEvent(report))
