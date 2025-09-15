from pathlib import Path

import pytest
from baby_steps import given, then, when
from pytest import raises

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

__all__ = ("dispatcher", "skipper", "tmp_dir",)  # fixtures


@pytest.mark.usefixtures(skipper.__name__)
async def test_select_scenario_by_line_number(*, dispatcher: Dispatcher, tmp_dir: Path):
    with given:
        file_path = touch(tmp_dir / "scenarios/scn.py")
        scenarios = [
            make_vscenario(file_path, name="Scenario1", lineno=10),
            make_vscenario(file_path, name="Scenario2", lineno=20),
            make_vscenario(file_path, name="Scenario3", lineno=30),
        ]

        await fire_arg_parsed_event(dispatcher, file_or_dir=[
            f"{file_path}:20"
        ])

        scheduler = Scheduler(scenarios)
        startup_event = StartupEvent(scheduler)

    with when:
        await dispatcher.fire(startup_event)

    with then:
        assert list(scheduler.scheduled) == [scenarios[1]]
        assert get_skipped(scheduler.scheduled) == []


@pytest.mark.usefixtures(skipper.__name__)
async def test_select_multiple_scenarios_by_line_numbers(*, dispatcher: Dispatcher, tmp_dir: Path):
    with given:
        file1 = touch(tmp_dir / "scenarios/scn1.py")
        file2 = touch(tmp_dir / "scenarios/scn2.py")
        scenarios = [
            make_vscenario(file1, name="Scenario1", lineno=5),
            make_vscenario(file1, name="Scenario2", lineno=15),
            make_vscenario(file2, name="Scenario3", lineno=10),
            make_vscenario(file2, name="Scenario4", lineno=25),
        ]

        # Select specific scenarios by line numbers
        await fire_arg_parsed_event(dispatcher, file_or_dir=[
            f"{file1}:15",
            f"{file2}:10"
        ])

        scheduler = Scheduler(scenarios)
        startup_event = StartupEvent(scheduler)

    with when:
        await dispatcher.fire(startup_event)

    with then:
        assert list(scheduler.scheduled) == [scenarios[1], scenarios[2]]
        assert get_skipped(scheduler.scheduled) == []


@pytest.mark.usefixtures(skipper.__name__)
async def test_line_number_not_matching_any_scenario(*, dispatcher: Dispatcher, tmp_dir: Path):
    with given:
        file_path = touch(tmp_dir / "scenarios/scn.py")
        scenarios = [
            make_vscenario(file_path, name="Scenario1", lineno=10),
            make_vscenario(file_path, name="Scenario2", lineno=20),
        ]

        await fire_arg_parsed_event(dispatcher, file_or_dir=[
            f"{file_path}:99"
        ])

        scheduler = Scheduler(scenarios)
        startup_event = StartupEvent(scheduler)

    with when:
        await dispatcher.fire(startup_event)

    with then:
        assert list(scheduler.scheduled) == []
        assert get_skipped(scheduler.scheduled) == []


@pytest.mark.usefixtures(skipper.__name__)
async def test_ignore_scenario_by_line_number(*, dispatcher: Dispatcher, tmp_dir: Path):
    with given:
        file_path = touch(tmp_dir / "scenarios/scn.py")
        scenarios = [
            make_vscenario(file_path, name="Scenario1", lineno=10),
            make_vscenario(file_path, name="Scenario2", lineno=20),
            make_vscenario(file_path, name="Scenario3", lineno=30),
        ]

        await fire_arg_parsed_event(dispatcher, file_or_dir=[str(file_path)],
                                    ignore=[f"{file_path}:20"])

        scheduler = Scheduler(scenarios)
        startup_event = StartupEvent(scheduler)

    with when:
        await dispatcher.fire(startup_event)

    with then:
        assert list(scheduler.scheduled) == [scenarios[0], scenarios[2]]
        assert get_skipped(scheduler.scheduled) == []


@pytest.mark.usefixtures(skipper.__name__)
async def test_invalid_line_number_format(*, dispatcher: Dispatcher, tmp_dir: Path):
    with given:
        file_path = touch(tmp_dir / "scenarios/scn.py")

    with when, raises(ValueError) as exc:
        await fire_arg_parsed_event(dispatcher, file_or_dir=[
            f"{file_path}:abc"
        ])

    with then:
        assert exc.type is ValueError
        assert str(exc.value) == (
            f"Invalid line number format in '{file_path}:abc'. "
            "Expected an integer after ':', but got 'abc'."
        )
