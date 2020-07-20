import asyncio
import signal
import sys
from types import FrameType
from typing import Optional

from ._core import Runner
from ._params import params
from ._scenario import Scenario
from ._version import version
from .plugins.skipper import only, skip
from .plugins.validator import Validator

__version__ = version
__all__ = ("Scenario", "Runner", "run", "only", "skip", "params",)


def run(*, validator: Optional[Validator] = None) -> None:
    runner = Runner(validator=validator)
    event = asyncio.Event()

    def signal_handler(sig: int, frame: FrameType) -> None:
        event.set()
        sys.exit(1)
    signal.signal(signal.SIGINT, signal_handler)
    asyncio.run(runner.run(event))
