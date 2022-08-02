from pathlib import Path

import pytest
from baby_steps import given, then, when

from vedro.core import Dispatcher
from vedro.core import MonotonicScenarioScheduler as Scheduler
from vedro.events import StartupEvent

from ._utils import (
    dispatcher,
    fire_arg_parsed_event,
    get_skipped,
    make_vscenario,
    skipper,
    tmp_dir,
    touch,
)

__all__ = ("dispatcher", "skipper", "tmp_dir")


@pytest.mark.asyncio
@pytest.mark.usefixtures(skipper.__name__)
async def test_multi_same_name(*, dispatcher: Dispatcher, tmp_dir: Path):
    path = touch(tmp_dir / "scenarios/scn1.py")
    with given:
        scenarios = [
            make_vscenario(path, name="Scenario"),
            make_vscenario(path, name="Scenario"),
        ]

        await fire_arg_parsed_event(dispatcher, file_or_dir=["scenarios/scn1.py"])

        scheduler = Scheduler(scenarios)
        startup_event = StartupEvent(scheduler)

    with when:
        await dispatcher.fire(startup_event)

    with then:
        assert list(scheduler.scheduled) == [scenarios[-1]]  # first is overridden
        assert get_skipped(scheduler.scheduled) == []


@pytest.mark.asyncio
@pytest.mark.usefixtures(skipper.__name__)
async def test_multi_diff_name(*, dispatcher: Dispatcher, tmp_dir: Path):
    with given:
        path = touch(tmp_dir / "scenarios/scn1.py")
        scenarios = [
            make_vscenario(path, name="Scenario1"),
            make_vscenario(path, name="Scenario2"),
        ]

        await fire_arg_parsed_event(dispatcher, file_or_dir=["scenarios/scn1.py"])

        scheduler = Scheduler(scenarios)
        startup_event = StartupEvent(scheduler)

    with when:
        await dispatcher.fire(startup_event)

    with then:
        assert list(scheduler.scheduled) == scenarios
        assert get_skipped(scheduler.scheduled) == []


@pytest.mark.asyncio
@pytest.mark.usefixtures(skipper.__name__)
@pytest.mark.parametrize(("scn_name1", "scn_name2"), [
    ("Scenario1", "Scenario2"),
    ("FirstScenario", "SecondScenario"),
])
async def test_multi_only_first(scn_name1: str, scn_name2: str, *,
                                dispatcher: Dispatcher, tmp_dir: Path):
    with given:
        path = touch(tmp_dir / "scenarios/scn1.py")
        scenarios = [
            make_vscenario(path, name=scn_name1),
            make_vscenario(path, name=scn_name2),
        ]

        await fire_arg_parsed_event(dispatcher, file_or_dir=[f"scenarios/scn1.py::{scn_name1}"])

        scheduler = Scheduler(scenarios)
        startup_event = StartupEvent(scheduler)

    with when:
        await dispatcher.fire(startup_event)

    with then:
        assert list(scheduler.scheduled) == [scenarios[0]]
        assert get_skipped(scheduler.scheduled) == []


@pytest.mark.asyncio
@pytest.mark.usefixtures(skipper.__name__)
async def test_multi_nonexisting(*, dispatcher: Dispatcher, tmp_dir: Path):
    with given:
        path = touch(tmp_dir / "scenarios/scn1.py")
        scenarios = [
            make_vscenario(path, name="Scenario1"),
            make_vscenario(path, name="Scenario2"),
        ]

        await fire_arg_parsed_event(dispatcher, file_or_dir=["scenarios/scn1.py::Scenario"])

        scheduler = Scheduler(scenarios)
        startup_event = StartupEvent(scheduler)

    with when:
        await dispatcher.fire(startup_event)

    with then:
        assert list(scheduler.scheduled) == []
