from argparse import ArgumentParser, Namespace
from pathlib import Path
from time import monotonic_ns
from typing import List, Optional

import pytest

from vedro import Scenario
from vedro.core import Dispatcher, VirtualScenario
from vedro.events import ArgParsedEvent, ArgParseEvent
from vedro.plugins.tagger import Tagger, TaggerPlugin


@pytest.fixture()
def dispatcher() -> Dispatcher:
    return Dispatcher()


@pytest.fixture()
def tagger(dispatcher: Dispatcher) -> TaggerPlugin:
    tagger = TaggerPlugin(Tagger)
    tagger.subscribe(dispatcher)
    return tagger


def make_vscenario(*, tags: Optional[List[str]] = None,
                   is_skipped: bool = False) -> VirtualScenario:
    class _Scenario(Scenario):
        __file__ = Path(f"scenario_{monotonic_ns()}.py").absolute()

    if tags is not None:
        _Scenario.tags = tags

    vscenario = VirtualScenario(_Scenario, steps=[])
    if is_skipped:
        vscenario.skip()
    return vscenario


async def fire_arg_parsed_event(dispatcher: Dispatcher, *, tags: Optional[str] = None) -> None:
    arg_parse_event = ArgParseEvent(ArgumentParser())
    await dispatcher.fire(arg_parse_event)

    arg_parsed_event = ArgParsedEvent(Namespace(tags=tags))
    await dispatcher.fire(arg_parsed_event)
