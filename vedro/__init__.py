import asyncio
from asyncio import CancelledError
from typing import List, Optional

from ._config import Config
from ._context import context
from ._interface import Interface
from ._params import params
from ._scenario import Scenario
from ._version import version
from .core import Dispatcher, Lifecycle, Plugin, Runner, ScenarioDiscoverer
from .core._config_loader import ConfigFileLoader
from .core._scenario_finder import ScenarioFileFinder
from .core._scenario_finder._file_filters import AnyFilter, DunderFilter, ExtFilter, HiddenFilter
from .core._scenario_loader import ScenarioAssertRewriterLoader
from .plugins.deferrer import defer
from .plugins.skipper import only, skip

__version__ = version
__all__ = ("Scenario", "Interface", "Runner", "run", "only", "skip", "params",
           "context", "defer", "Config",)


def run(*, plugins: Optional[List[Plugin]] = None) -> None:
    if plugins is not None:
        raise DeprecationWarning("Argument 'plugins' is deprecated, "
                                 "declare plugins in config (vedro.cfg.py)")

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
    discoverer = ScenarioDiscoverer(finder, ScenarioAssertRewriterLoader())
    dispatcher = Dispatcher()
    runner = Runner(dispatcher, (KeyboardInterrupt, SystemExit, CancelledError,))
    lifecycle = Lifecycle(dispatcher, discoverer, runner, ConfigFileLoader(Config))

    asyncio.run(lifecycle.start())
