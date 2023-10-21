from argparse import ArgumentParser, Namespace
from pathlib import Path
from random import random
from time import monotonic_ns
from typing import List, Optional

import pytest

from vedro import Scenario
from vedro.core import Dispatcher
from vedro.core import MonotonicScenarioScheduler as Scheduler
from vedro.core import ScenarioResult, VirtualScenario
from vedro.events import ArgParsedEvent, ArgParseEvent, ScenarioRunEvent, StartupEvent
from vedro.plugins.seeder import Seeder, SeederPlugin


@pytest.fixture()
def dispatcher() -> Dispatcher:
    return Dispatcher()


@pytest.fixture()
def seeder(dispatcher: Dispatcher) -> SeederPlugin:
    seeder = SeederPlugin(Seeder)
    seeder.subscribe(dispatcher)
    return seeder


def make_vscenario(*, is_skipped: bool = False) -> VirtualScenario:
    class _Scenario(Scenario):
        __file__ = Path(f"scenario_{monotonic_ns()}.py").absolute()

    vscenario = VirtualScenario(_Scenario, steps=[])
    if is_skipped:
        vscenario.skip()
    return vscenario


def make_scenario_result(vscenario: Optional[VirtualScenario] = None) -> ScenarioResult:
    return ScenarioResult(vscenario or make_vscenario())


async def fire_arg_parsed_event(dispatcher: Dispatcher, *, seed: Optional[str] = None) -> None:
    arg_parse_event = ArgParseEvent(ArgumentParser())
    await dispatcher.fire(arg_parse_event)

    arg_parsed_event = ArgParsedEvent(Namespace(seed=seed, fixed_seed=False))
    await dispatcher.fire(arg_parsed_event)


async def fire_startup_event(dispatcher: Dispatcher, scheduler: Scheduler) -> None:
    startup_event = StartupEvent(scheduler)
    await dispatcher.fire(startup_event)


def generate_random() -> int:
    return int(random() * 10 ** 6)


async def run_scenarios(dispatcher: Dispatcher, scheduler: Scheduler) -> List[int]:
    generated = []
    async for vscenario in scheduler:
        event = ScenarioRunEvent(ScenarioResult(vscenario))
        await dispatcher.fire(event)
        generated.append(generate_random())
    return generated
