import asyncio
import os
import sys
from typing import List, Optional

from ._config import Config
from ._context import context
from ._interface import Interface
from ._params import params
from ._scenario import Scenario
from ._version import version
from .core import ConfigFileLoader, Lifecycle, Plugin
from .plugins.deferrer import defer
from .plugins.skipper import only, skip, skip_if

__version__ = version
__all__ = ("Scenario", "Interface", "run", "only", "skip", "skip_if", "params",
           "context", "defer", "Config",)


def run(*, plugins: Optional[List[Plugin]] = None) -> None:
    if plugins is not None:
        raise DeprecationWarning("Argument 'plugins' is deprecated, "
                                 "declare plugins in config (vedro.cfg.py)")

    cwd = os.getcwd()
    if cwd not in sys.path:
        sys.path.insert(0, cwd)

    lifecycle = Lifecycle(ConfigFileLoader(Config))
    asyncio.run(lifecycle.start())
