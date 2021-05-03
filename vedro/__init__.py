import asyncio
import signal
import sys
from types import FrameType
from typing import Optional

from ._context import context
from ._core import Runner, ScenarioDiscoverer
from ._core._scenario_finder import ScenarioFileFinder
from ._core._scenario_finder._file_filters import AnyFilter, DunderFilter, ExtFilter, HiddenFilter
from ._core._scenario_loader import ScenarioFileLoader
from ._interface import Interface
from ._params import params
from ._scenario import Scenario
from ._version import version
from .plugins.skipper import only, skip
from .plugins.validator import Validator

__version__ = version
__all__ = ("Scenario", "Interface", "Runner", "run", "only", "skip", "params", "context",)


def run(*, validator: Optional[Validator] = None) -> None:
    finder = ScenarioFileFinder(
        file_filter=AnyFilter([
            HiddenFilter(),
            DunderFilter(),
            ExtFilter(only=["py"]),
        ]),
        dir_filter=AnyFilter([
            HiddenFilter(),
            DunderFilter(),
        ])
    )
    loader = ScenarioFileLoader()
    discoverer = ScenarioDiscoverer(finder, loader)

    runner = Runner(discoverer, validator=validator)
    event = asyncio.Event()

    def signal_handler(sig: int, frame: FrameType) -> None:
        event.set()
        sys.exit(1)
    signal.signal(signal.SIGINT, signal_handler)
    asyncio.run(runner.run(event))
