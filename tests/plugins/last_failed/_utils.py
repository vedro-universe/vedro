from argparse import ArgumentParser, Namespace
from pathlib import Path
from time import monotonic_ns
from typing import Optional, Tuple, Union, cast

import pytest

from vedro import Config, Scenario
from vedro.core import AggregatedResult, Dispatcher, ScenarioResult, VirtualScenario
from vedro.core.exp.local_storage import LocalStorage, create_local_storage
from vedro.events import ArgParsedEvent, ArgParseEvent, ConfigLoadedEvent, ScenarioReportedEvent
from vedro.plugins.last_failed import LastFailed, LastFailedPlugin


@pytest.fixture()
def dispatcher() -> Dispatcher:
    return Dispatcher()


@pytest.fixture()
async def last_failed_storage(dispatcher: Dispatcher,
                              tmp_path: Path) -> Tuple[LastFailedPlugin, LocalStorage]:
    local_storage = None

    def _create_local_storage(*args, **kwargs) -> LocalStorage:
        nonlocal local_storage
        local_storage = create_local_storage(*args, **kwargs)
        return local_storage

    plugin = LastFailedPlugin(LastFailed, local_storage_factory=_create_local_storage)
    plugin.subscribe(dispatcher)

    await fire_config_loaded_event(dispatcher, tmp_path)

    return plugin, cast(LocalStorage, local_storage)


@pytest.fixture()
def last_failed(last_failed_storage: Tuple[LastFailedPlugin, LocalStorage]) -> LastFailedPlugin:
    plugin, *_ = last_failed_storage
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


async def fire_config_loaded_event(dispatcher: Dispatcher, tmp_path: Path) -> None:
    class _Config(Config):
        project_dir = tmp_path

    config_loaded_event = ConfigLoadedEvent(_Config.project_dir, _Config)
    await dispatcher.fire(config_loaded_event)


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
