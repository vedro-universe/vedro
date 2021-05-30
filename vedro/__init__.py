import asyncio
from typing import List, Optional

from ._context import context
from ._core import Runner, ScenarioDiscoverer
from ._core._dispatcher import Dispatcher
from ._core._lifecycle import Lifecycle
from ._core._scenario_finder import ScenarioFileFinder
from ._core._scenario_finder._file_filters import AnyFilter, DunderFilter, ExtFilter, HiddenFilter
from ._core._scenario_loader import ScenarioFileLoader
from ._interface import Interface
from ._params import params
from ._scenario import Scenario
from ._version import version
from .plugins import Plugin
from .plugins.skipper import only, skip
from .plugins.validator import Validator

__version__ = version
__all__ = ("Scenario", "Interface", "Runner", "run", "only", "skip", "params", "context",)


def run(*, validator: Optional[Validator] = None, plugins: Optional[List[Plugin]] = None) -> None:
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
    dispatcher = Dispatcher()

    lifecycle = Lifecycle(dispatcher, discoverer, plugins)
    asyncio.run(lifecycle.start())
