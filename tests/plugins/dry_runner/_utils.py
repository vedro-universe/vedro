import sys
from argparse import ArgumentParser, Namespace
from pathlib import Path
from time import monotonic_ns
from typing import Any, Callable, List, Optional, Type

import pytest

from vedro import Scenario
from vedro.core import (
    AggregatedResult,
    Config,
    ConfigType,
    Dispatcher,
    Factory,
    ScenarioResult,
    ScenarioRunner,
    VirtualScenario,
    VirtualStep,
)
from vedro.events import ArgParsedEvent, ArgParseEvent, ConfigLoadedEvent
from vedro.plugins.dry_runner import DryRunner, DryRunnerImpl, DryRunnerPlugin

if sys.version_info >= (3, 8):
    from unittest.mock import AsyncMock
else:
    from asynctest.mock import CoroutineMock as AsyncMock


__all__ = ("dispatcher_", "dispatcher", "dry_runner", "interrupt_exception",
           "make_vstep", "make_vscenario", "make_scenario_result", "make_aggregated_result",
           "dry_runner_plugin", "make_config", "fire_arg_parsed_event",
           "fire_config_loaded_event",)


@pytest.fixture()
def dispatcher_():
    return AsyncMock(Dispatcher())


@pytest.fixture()
def interrupt_exception():
    class InterruptException(KeyboardInterrupt):
        pass

    return InterruptException


@pytest.fixture()
def dry_runner(dispatcher_: Dispatcher, interrupt_exception: Type[BaseException]):
    interrupt_exceptions = (interrupt_exception,)
    return DryRunnerImpl(dispatcher_, interrupt_exceptions=interrupt_exceptions)


@pytest.fixture()
def dispatcher():
    return Dispatcher()


@pytest.fixture()
def dry_runner_plugin(dispatcher: Dispatcher) -> DryRunnerPlugin:
    plugin = DryRunnerPlugin(DryRunner)
    plugin.subscribe(dispatcher)
    return plugin


def make_vstep(callable: Callable[..., Any] = None, *, name: Optional[str] = None) -> VirtualStep:
    def step(self):
        if callable:
            callable(self)
    step.__name__ = name or f"step_{monotonic_ns()}"
    return VirtualStep(step)


def make_vscenario(steps: Optional[List[VirtualStep]] = None, *,
                   is_skipped: bool = False) -> VirtualScenario:
    class _Scenario(Scenario):
        __file__ = Path(f"scenario_{monotonic_ns()}.py").absolute()

    vsenario = VirtualScenario(_Scenario, steps=steps or [])
    if is_skipped:
        vsenario.skip()
    return vsenario


def make_scenario_result() -> ScenarioResult:
    return ScenarioResult(make_vscenario())


def make_aggregated_result(scenario_result: Optional[ScenarioResult] = None) -> AggregatedResult:
    if scenario_result is None:
        scenario_result = make_scenario_result()
    return AggregatedResult.from_existing(scenario_result, [scenario_result])


def make_config(dispatcher: Dispatcher, scenario_runner: ScenarioRunner) -> ConfigType:
    class TestConfig(Config):
        class Registry(Config.Registry):
            Dispatcher = Factory[Dispatcher](lambda: dispatcher)
            ScenarioRunner = Factory[ScenarioRunner](lambda: scenario_runner)

    return TestConfig


async def fire_config_loaded_event(dispatcher: Dispatcher, config: ConfigType) -> None:
    config_loaded_event = ConfigLoadedEvent(Path(), config)
    await dispatcher.fire(config_loaded_event)


async def fire_arg_parsed_event(dispatcher: Dispatcher, *, dry_run: bool) -> None:
    arg_parse_event = ArgParseEvent(ArgumentParser())
    await dispatcher.fire(arg_parse_event)

    arg_parsed_event = ArgParsedEvent(Namespace(dry_run=dry_run))
    await dispatcher.fire(arg_parsed_event)
