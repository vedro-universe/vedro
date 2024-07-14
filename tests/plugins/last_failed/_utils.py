from argparse import ArgumentParser, Namespace
from pathlib import Path
from time import monotonic_ns
from typing import Callable, Optional, Tuple, Union, cast

import pytest

from vedro import Config, Scenario
from vedro.core import AggregatedResult, Dispatcher, ScenarioResult, VirtualScenario
from vedro.core.exp.local_storage import LocalStorage, create_local_storage
from vedro.events import ArgParsedEvent, ArgParseEvent, ConfigLoadedEvent, ScenarioReportedEvent
from vedro.plugins.last_failed import LastFailed, LastFailedPlugin


@pytest.fixture()
def dispatcher() -> Dispatcher:
    return Dispatcher()


def make_last_failed(dispatcher: Dispatcher
                     ) -> Tuple[LastFailedPlugin, Callable[[], LocalStorage]]:
    local_storage = None

    def _create_local_storage(*args, **kwargs) -> LocalStorage:
        nonlocal local_storage
        local_storage = create_local_storage(*args, **kwargs)
        return local_storage

    def _get_local_storage() -> LocalStorage:
        nonlocal local_storage
        return cast(LocalStorage, local_storage)

    plugin = LastFailedPlugin(LastFailed, local_storage_factory=_create_local_storage)
    plugin.subscribe(dispatcher)
    return plugin, _get_local_storage


@pytest.fixture()
def last_failed(dispatcher: Dispatcher) -> LastFailedPlugin:
    plugin, *_ = make_last_failed(dispatcher)
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


async def fire_arg_parsed_event(dispatcher: Dispatcher, tmp_path: Path, *,
                                last_failed: Union[bool, None] = None) -> None:
    class _Config(Config):
        project_dir = tmp_path

    config_loaded_event = ConfigLoadedEvent(_Config.project_dir, _Config)
    await dispatcher.fire(config_loaded_event)

    arg_parse_event = ArgParseEvent(ArgumentParser())
    await dispatcher.fire(arg_parse_event)

    arg_parsed_event = ArgParsedEvent(Namespace(last_failed=last_failed))
    await dispatcher.fire(arg_parsed_event)


async def fire_scenario_reported_event(dispatcher: Dispatcher,
                                       scenario_result: ScenarioResult) -> None:
    aggregated_result = make_aggregated_result(scenario_result)
    await dispatcher.fire(ScenarioReportedEvent(aggregated_result))
