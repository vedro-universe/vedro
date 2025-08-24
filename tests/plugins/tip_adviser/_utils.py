from argparse import Namespace
from typing import Any

import pytest

from vedro.core import Dispatcher
from vedro.events import ArgParsedEvent
from vedro.plugins.tip_adviser import TipAdviser, TipAdviserPlugin

__all__ = ("dispatcher", "tip_adviser", "fire_arg_parsed_event",)


@pytest.fixture()
def dispatcher() -> Dispatcher:
    return Dispatcher()


@pytest.fixture()
def tip_adviser(dispatcher: Dispatcher) -> TipAdviserPlugin:
    tip_adviser = TipAdviserPlugin(TipAdviser)
    tip_adviser.subscribe(dispatcher)
    return tip_adviser


async def fire_arg_parsed_event(dispatcher: Dispatcher, **kwargs: Any) -> None:
    args = Namespace(**kwargs)
    await dispatcher.fire(ArgParsedEvent(args))
