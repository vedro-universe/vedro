from argparse import ArgumentParser, Namespace
from pathlib import Path
from time import monotonic_ns
from typing import Union

import pytest

from vedro import Scenario
from vedro.core import Dispatcher, VirtualScenario
from vedro.events import ArgParsedEvent, ArgParseEvent
from vedro.plugins.slicer import Slicer, SlicerPlugin


@pytest.fixture()
def dispatcher() -> Dispatcher:
    return Dispatcher()


@pytest.fixture()
def slicer(dispatcher: Dispatcher) -> SlicerPlugin:
    slicer = SlicerPlugin(Slicer)
    slicer.subscribe(dispatcher)
    return slicer


def make_vscenario(*, is_skipped: bool = False) -> VirtualScenario:
    class _Scenario(Scenario):
        __file__ = Path(f"scenario_{monotonic_ns()}.py").absolute()

    vsenario = VirtualScenario(_Scenario, steps=[])
    if is_skipped:
        vsenario.skip()
    return vsenario


async def fire_arg_parsed_event(dispatcher: Dispatcher, *,
                                total: Union[int, None] = None,
                                index: Union[int, None] = None) -> None:
    arg_parse_event = ArgParseEvent(ArgumentParser())
    await dispatcher.fire(arg_parse_event)

    arg_parsed_event = ArgParsedEvent(Namespace(slicer_total=total, slicer_index=index))
    await dispatcher.fire(arg_parsed_event)
