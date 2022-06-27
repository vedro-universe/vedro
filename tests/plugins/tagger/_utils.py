import os
from argparse import ArgumentParser, Namespace
from time import monotonic_ns
from typing import List, Optional
from unittest.mock import Mock

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


def make_virtual_scenario(*, tags: Optional[List[str]] = None) -> VirtualScenario:
    scenario_ = Mock(spec=Scenario)
    scenario_.__file__ = os.getcwd() + f"/scenarios/scenario_{monotonic_ns()}.py"
    scenario_.__name__ = "Scenario"
    if tags is not None:
        scenario_.tags = tags

    return VirtualScenario(scenario_, steps=[])


async def fire_arg_parsed_event(dispatcher: Dispatcher, *, tags: Optional[str] = None) -> None:
    arg_parse_event = ArgParseEvent(ArgumentParser())
    await dispatcher.fire(arg_parse_event)

    arg_parsed_event = ArgParsedEvent(Namespace(tags=tags))
    await dispatcher.fire(arg_parsed_event)
