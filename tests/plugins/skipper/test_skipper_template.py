from pathlib import Path
from time import monotonic_ns

import pytest
from baby_steps import given, then, when

import vedro
from vedro.core import Dispatcher
from vedro.core import MonotonicScenarioScheduler as Scheduler
from vedro.events import StartupEvent

from ._utils import (
    dispatcher,
    fire_arg_parsed_event,
    get_skipped,
    make_template_vscenario,
    skipper,
    tmp_dir,
    touch,
)

__all__ = ("dispatcher", "skipper", "tmp_dir",)  # fixtures


@pytest.mark.usefixtures(skipper.__name__, tmp_dir.__name__)
async def test_template_default(*, dispatcher: Dispatcher):
    with given:
        @vedro.params()
        @vedro.params()
        def __init__(self):
            pass
        _, scenarios = make_template_vscenario(__init__)

        await fire_arg_parsed_event(dispatcher)

        scheduler = Scheduler(scenarios)
        startup_event = StartupEvent(scheduler)

    with when:
        await dispatcher.fire(startup_event)

    with then:
        assert list(scheduler.scheduled) == scenarios
        assert get_skipped(scheduler.scheduled) == []


@pytest.mark.usefixtures(skipper.__name__)
async def test_template_path(*, dispatcher: Dispatcher, tmp_dir: Path):
    with given:
        @vedro.params()
        @vedro.params()
        def __init__(self):
            pass

        path = touch(tmp_dir / "scenarios/scn1.py")
        _, scenarios = make_template_vscenario(__init__, path=path)

        await fire_arg_parsed_event(dispatcher)

        scheduler = Scheduler(scenarios)
        startup_event = StartupEvent(scheduler)

    with when:
        await dispatcher.fire(startup_event)

    with then:
        assert list(scheduler.scheduled) == scenarios
        assert get_skipped(scheduler.scheduled) == []


@pytest.mark.usefixtures(skipper.__name__)
async def test_template_path_name(*, dispatcher: Dispatcher, tmp_dir: Path):
    with given:
        @vedro.params()
        @vedro.params()
        def __init__(self):
            pass

        path = touch(tmp_dir / "scenarios/scn1.py")
        name = f"Scenario_{monotonic_ns()}"
        _, scenarios = make_template_vscenario(__init__, path=path, name=name)

        await fire_arg_parsed_event(dispatcher, file_or_dir=[f"{path}::{name}"])

        scheduler = Scheduler(scenarios)
        startup_event = StartupEvent(scheduler)

    with when:
        await dispatcher.fire(startup_event)

    with then:
        assert list(scheduler.scheduled) == scenarios
        assert get_skipped(scheduler.scheduled) == []


@pytest.mark.usefixtures(skipper.__name__)
async def test_template_path_not_name(*, dispatcher: Dispatcher, tmp_dir: Path):
    with given:
        @vedro.params()
        @vedro.params()
        def __init__(self):
            pass

        path = touch(tmp_dir / "scenarios/scn1.py")
        name = f"Scenario_{monotonic_ns()}"
        _, scenarios = make_template_vscenario(__init__, path=path, name=name)

        await fire_arg_parsed_event(dispatcher, file_or_dir=[f"{path}::Scenario"])

        scheduler = Scheduler(scenarios)
        startup_event = StartupEvent(scheduler)

    with when:
        await dispatcher.fire(startup_event)

    with then:
        assert list(scheduler.scheduled) == []
        assert get_skipped(scheduler.scheduled) == []


@pytest.mark.usefixtures(skipper.__name__)
@pytest.mark.parametrize("index", [1, 2])
async def test_template_path_name_index(index: int, *, dispatcher: Dispatcher, tmp_dir: Path):
    with given:
        @vedro.params()
        @vedro.params()
        def __init__(self):
            pass

        path = touch(tmp_dir / "scenarios/scn1.py")
        name = f"Scenario_{monotonic_ns()}"
        _, scenarios = make_template_vscenario(__init__, path=path, name=name)

        await fire_arg_parsed_event(dispatcher, file_or_dir=[f"{path}::{name}#{index}"])

        scheduler = Scheduler(scenarios)
        startup_event = StartupEvent(scheduler)

    with when:
        await dispatcher.fire(startup_event)

    with then:
        assert list(scheduler.scheduled) == [scenarios[index - 1]]
        assert get_skipped(scheduler.scheduled) == []


@pytest.mark.usefixtures(skipper.__name__)
@pytest.mark.parametrize("index", [0, 3])
async def test_template_path_name_not_index(index: int, *, dispatcher: Dispatcher, tmp_dir: Path):
    with given:
        @vedro.params()
        @vedro.params()
        def __init__(self):
            pass

        path = touch(tmp_dir / "scenarios/scn1.py")
        name = f"Scenario_{monotonic_ns()}"
        _, scenarios = make_template_vscenario(__init__, path=path, name=name)

        await fire_arg_parsed_event(dispatcher, file_or_dir=[f"{path}::{name}#{index}"])

        scheduler = Scheduler(scenarios)
        startup_event = StartupEvent(scheduler)

    with when:
        await dispatcher.fire(startup_event)

    with then:
        assert list(scheduler.scheduled) == []
        assert get_skipped(scheduler.scheduled) == []
