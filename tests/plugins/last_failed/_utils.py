from argparse import ArgumentParser, Namespace
from pathlib import Path
from time import monotonic_ns
from typing import Optional, Tuple, Union, cast

import pytest

from vedro import Scenario
from vedro.core import AggregatedResult, Dispatcher, Plugin, ScenarioResult, VirtualScenario
from vedro.core.exp.local_storage import LocalStorage
from vedro.events import ArgParsedEvent, ArgParseEvent, ScenarioReportedEvent
from vedro.plugins.last_failed import LastFailed, LastFailedPlugin


@pytest.fixture()
def dispatcher() -> Dispatcher:
    return Dispatcher()


def make_last_failed(dispatcher: Dispatcher,
                     tmp_path: Path) -> Tuple[LastFailedPlugin, LocalStorage]:
    local_storage = None

    def create_local_storage(plugin: Plugin):
        nonlocal local_storage
        local_storage = LocalStorage(plugin, tmp_path)
        return local_storage

    plugin = LastFailedPlugin(LastFailed, local_storage_factory=create_local_storage)
    plugin.subscribe(dispatcher)
    return plugin, cast(LocalStorage, local_storage)


@pytest.fixture()
def last_failed(dispatcher: Dispatcher, tmp_path: Path) -> LastFailedPlugin:
    plugin, *_ = make_last_failed(dispatcher, tmp_path)
    return plugin


def make_vscenario() -> VirtualScenario:
    class _Scenario(Scenario):
        __file__ = Path(f"scenario_{monotonic_ns()}.py").absolute()

    return VirtualScenario(_Scenario, steps=[])


def make_scenario_result(vscenario: Optional[VirtualScenario] = None) -> ScenarioResult:
    return ScenarioResult(vscenario or make_vscenario())


def make_aggregated_result(scenario_result: Optional[ScenarioResult] = None) -> AggregatedResult:
    if scenario_result is None:
        scenario_result = make_scenario_result()
    return AggregatedResult.from_existing(scenario_result, [scenario_result])


async def fire_arg_parsed_event(dispatcher: Dispatcher, *,
                                last_failed: Union[bool, None] = None) -> None:
    arg_parse_event = ArgParseEvent(ArgumentParser())
    await dispatcher.fire(arg_parse_event)

    arg_parsed_event = ArgParsedEvent(Namespace(last_failed=last_failed))
    await dispatcher.fire(arg_parsed_event)


async def fire_scenario_reported_event(dispatcher: Dispatcher,
                                       scenario_result: ScenarioResult) -> None:
    aggregated_result = make_aggregated_result(scenario_result)
    await dispatcher.fire(ScenarioReportedEvent(aggregated_result))
