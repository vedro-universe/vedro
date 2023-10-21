from os import getcwd
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

__all__ = ("dispatcher", "skipper", "tmp_dir",)  # fixtures


@pytest.mark.usefixtures(skipper.__name__, tmp_dir.__name__)
async def test_defaults(*, dispatcher: Dispatcher):
    with given:
        scenarios = [
            make_vscenario(),
            make_vscenario(),
        ]

        await fire_arg_parsed_event(dispatcher)

        scheduler = Scheduler(scenarios)
        startup_event = StartupEvent(scheduler)

    with when:
        await dispatcher.fire(startup_event)

    with then:
        assert list(scheduler.scheduled) == scenarios
        assert get_skipped(scheduler.scheduled) == []


@pytest.mark.usefixtures(skipper.__name__)
async def test_select_single_file(*, dispatcher: Dispatcher, tmp_dir: Path):
    with given:
        scenarios = [
            make_vscenario(touch(tmp_dir / "scenarios/dir1/scn1.py")),
            make_vscenario(touch(tmp_dir / "scenarios/dir1/scn2.py")),
            make_vscenario(touch(tmp_dir / "scenarios/dir2/scn1.py")),
            make_vscenario(touch(tmp_dir / "scenarios/scn1.py"))
        ]

        await fire_arg_parsed_event(dispatcher, file_or_dir=[
            str(scenarios[0].path)
        ])

        scheduler = Scheduler(scenarios)
        startup_event = StartupEvent(scheduler)

    with when:
        await dispatcher.fire(startup_event)

    with then:
        assert list(scheduler.scheduled) == [scenarios[0]]
        assert get_skipped(scheduler.scheduled) == []


@pytest.mark.usefixtures(skipper.__name__)
async def test_select_multiple_files(*, dispatcher: Dispatcher, tmp_dir: Path):
    with given:
        scenarios = [
            make_vscenario(touch(tmp_dir / "scenarios/dir1/scn1.py")),
            make_vscenario(touch(tmp_dir / "scenarios/dir1/scn2.py")),
            make_vscenario(touch(tmp_dir / "scenarios/dir2/scn1.py")),
            make_vscenario(touch(tmp_dir / "scenarios/scn1.py"))
        ]

        await fire_arg_parsed_event(dispatcher, file_or_dir=[
            str(scenarios[0].path),
            str(scenarios[2].path),
        ])

        scheduler = Scheduler(scenarios)
        startup_event = StartupEvent(scheduler)

    with when:
        await dispatcher.fire(startup_event)

    with then:
        assert list(scheduler.scheduled) == [scenarios[0], scenarios[2]]
        assert get_skipped(scheduler.scheduled) == []


@pytest.mark.usefixtures(skipper.__name__)
async def test_select_dir(*, dispatcher: Dispatcher, tmp_dir: Path):
    with given:
        scenarios = [
            make_vscenario(touch(tmp_dir / "scenarios/dir1/scn1.py")),
            make_vscenario(touch(tmp_dir / "scenarios/dir1/scn2.py")),
            make_vscenario(touch(tmp_dir / "scenarios/dir2/scn1.py")),
            make_vscenario(touch(tmp_dir / "scenarios/scn1.py"))
        ]

        await fire_arg_parsed_event(dispatcher, file_or_dir=[
            str(tmp_dir / "scenarios/dir1")
        ])

        scheduler = Scheduler(scenarios)
        startup_event = StartupEvent(scheduler)

    with when:
        await dispatcher.fire(startup_event)

    with then:
        assert list(scheduler.scheduled) == [scenarios[0], scenarios[1]]
        assert get_skipped(scheduler.scheduled) == []


@pytest.mark.usefixtures(skipper.__name__)
@pytest.mark.parametrize("dirname", ["dir1", "scenarios/dir1"])
async def test_select_rel_dir(dirname: str, *, dispatcher: Dispatcher, tmp_dir: Path):
    with given:
        scenarios = [
            make_vscenario(touch(tmp_dir / "scenarios/dir1/scn1.py")),
            make_vscenario(touch(tmp_dir / "scenarios/dir1/scn2.py")),
            make_vscenario(touch(tmp_dir / "scenarios/dir2/scn1.py")),
            make_vscenario(touch(tmp_dir / "scenarios/scn1.py"))
        ]

        rel_path = tmp_dir.relative_to(getcwd())
        await fire_arg_parsed_event(dispatcher, file_or_dir=[
            str(rel_path / dirname)
        ])

        scheduler = Scheduler(scenarios)
        startup_event = StartupEvent(scheduler)

    with when:
        await dispatcher.fire(startup_event)

    with then:
        assert list(scheduler.scheduled) == [scenarios[0], scenarios[1]]
        assert get_skipped(scheduler.scheduled) == []


@pytest.mark.usefixtures(skipper.__name__, tmp_dir.__name__)
async def test_single_subject(*, dispatcher: Dispatcher):
    with given:
        subject = "subject1"
        await fire_arg_parsed_event(dispatcher, subject=subject)

        scenarios = [
            make_vscenario(subject=subject),
            make_vscenario(subject="subject2"),
        ]
        scheduler = Scheduler(scenarios)
        startup_event = StartupEvent(scheduler)

    with when:
        await dispatcher.fire(startup_event)

    with then:
        assert list(scheduler.scheduled) == [scenarios[0]]
        assert get_skipped(scheduler.scheduled) == []


@pytest.mark.usefixtures(skipper.__name__, tmp_dir.__name__)
async def test_multiple_subjects(*, dispatcher: Dispatcher):
    with given:
        subject = "subject1"
        await fire_arg_parsed_event(dispatcher, subject=subject)

        scenarios = [
            make_vscenario(subject=subject),
            make_vscenario(subject="subject2"),
            make_vscenario(subject=subject),
        ]
        scheduler = Scheduler(scenarios)
        startup_event = StartupEvent(scheduler)

    with when:
        await dispatcher.fire(startup_event)

    with then:
        assert list(scheduler.scheduled) == [scenarios[0], scenarios[-1]]
        assert get_skipped(scheduler.scheduled) == []


@pytest.mark.usefixtures(skipper.__name__, tmp_dir.__name__)
async def test_single_only(*, dispatcher: Dispatcher):
    with given:
        await fire_arg_parsed_event(dispatcher)

        scenarios = [
            make_vscenario(only=True),
            make_vscenario(),
        ]
        scheduler = Scheduler(scenarios)
        startup_event = StartupEvent(scheduler)

    with when:
        await dispatcher.fire(startup_event)

    with then:
        assert list(scheduler.scheduled) == [scenarios[0]]
        assert get_skipped(scheduler.scheduled) == []


@pytest.mark.usefixtures(skipper.__name__, tmp_dir.__name__)
async def test_multiple_only(*, dispatcher: Dispatcher):
    with given:
        await fire_arg_parsed_event(dispatcher)

        scenarios = [
            make_vscenario(only=True),
            make_vscenario(),
            make_vscenario(),
            make_vscenario(only=True),
        ]
        scheduler = Scheduler(scenarios)
        startup_event = StartupEvent(scheduler)

    with when:
        await dispatcher.fire(startup_event)

    with then:
        assert list(scheduler.scheduled) == [scenarios[0], scenarios[3]]
        assert get_skipped(scheduler.scheduled) == []


@pytest.mark.usefixtures(skipper.__name__, tmp_dir.__name__)
async def test_single_skip(*, dispatcher: Dispatcher):
    with given:
        await fire_arg_parsed_event(dispatcher)

        scenarios = [
            make_vscenario(skip=True),
            make_vscenario(),
        ]
        scheduler = Scheduler(scenarios)
        startup_event = StartupEvent(scheduler)

    with when:
        await dispatcher.fire(startup_event)

    with then:
        assert list(scheduler.scheduled) == scenarios
        assert get_skipped(scheduler.scheduled) == [scenarios[0]]


@pytest.mark.usefixtures(skipper.__name__, tmp_dir.__name__)
async def test_multiple_skip(*, dispatcher: Dispatcher):
    with given:
        await fire_arg_parsed_event(dispatcher)

        scenarios = [
            make_vscenario(skip=True),
            make_vscenario(),
            make_vscenario(),
            make_vscenario(skip=True),
        ]
        scheduler = Scheduler(scenarios)
        startup_event = StartupEvent(scheduler)

    with when:
        await dispatcher.fire(startup_event)

    with then:
        assert list(scheduler.scheduled) == scenarios
        assert get_skipped(scheduler.scheduled) == [scenarios[0], scenarios[3]]
