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


# select

@pytest.mark.usefixtures(skipper.__name__)
async def test_select_dir_and_ignore_file(*, dispatcher: Dispatcher, tmp_dir: Path):
    with given:
        scenarios = [
            make_vscenario(touch(tmp_dir / "scenarios/dir1/scn1.py")),
            make_vscenario(touch(tmp_dir / "scenarios/dir1/scn2.py")),
            make_vscenario(touch(tmp_dir / "scenarios/dir2/scn1.py")),
            make_vscenario(touch(tmp_dir / "scenarios/scn1.py"))
        ]

        await fire_arg_parsed_event(dispatcher,
                                    file_or_dir=[str(tmp_dir / "scenarios/dir1")],
                                    ignore=[str(scenarios[0].path)]
                                    )

        scheduler = Scheduler(scenarios)
        startup_event = StartupEvent(scheduler)

    with when:
        await dispatcher.fire(startup_event)

    with then:
        assert list(scheduler.scheduled) == [scenarios[1]]
        assert get_skipped(scheduler.scheduled) == []


@pytest.mark.usefixtures(skipper.__name__)
async def test_select_file_and_ignore_file(*, dispatcher: Dispatcher, tmp_dir: Path):
    with given:
        scenarios = [
            make_vscenario(touch(tmp_dir / "scenarios/scn1.py")),
            make_vscenario(touch(tmp_dir / "scenarios/scn2.py")),
        ]

        await fire_arg_parsed_event(dispatcher,
                                    file_or_dir=[str(scenarios[0].path)],
                                    ignore=[str(scenarios[0].path)]
                                    )

        scheduler = Scheduler(scenarios)
        startup_event = StartupEvent(scheduler)

    with when:
        await dispatcher.fire(startup_event)

    with then:
        assert list(scheduler.scheduled) == []


@pytest.mark.usefixtures(skipper.__name__)
async def test_select_file_and_subject(*, dispatcher: Dispatcher, tmp_dir: Path):
    with given:
        subject = "subject"
        scenarios = [
            make_vscenario(touch(tmp_dir / "scenarios/scn1.py"), subject=subject),
            make_vscenario(touch(tmp_dir / "scenarios/scn2.py"), subject=subject),
        ]

        await fire_arg_parsed_event(dispatcher, subject=subject, file_or_dir=[
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
async def test_select_dir_and_subject(*, dispatcher: Dispatcher, tmp_dir: Path):
    with given:
        subject = "subject1"
        scenarios = [
            make_vscenario(touch(tmp_dir / "scenarios/dir1/scn1.py"), subject=subject),
            make_vscenario(touch(tmp_dir / "scenarios/dir1/scn2.py"), subject="subject2"),
            make_vscenario(touch(tmp_dir / "scenarios/dir1/scn3.py"), subject=subject),
            make_vscenario(touch(tmp_dir / "scenarios/scn1.py"), subject=subject)
        ]

        await fire_arg_parsed_event(dispatcher, subject=subject, file_or_dir=[
            str(tmp_dir / "scenarios/dir1")
        ])

        scheduler = Scheduler(scenarios)
        startup_event = StartupEvent(scheduler)

    with when:
        await dispatcher.fire(startup_event)

    with then:
        assert list(scheduler.scheduled) == [scenarios[0], scenarios[2]]
        assert get_skipped(scheduler.scheduled) == []


@pytest.mark.usefixtures(skipper.__name__)
async def test_select_file_and_only(*, dispatcher: Dispatcher, tmp_dir: Path):
    with given:
        scenarios = [
            make_vscenario(touch(tmp_dir / "scenarios/scn1.py"), only=True),
            make_vscenario(touch(tmp_dir / "scenarios/scn2.py"), only=True),
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
async def test_select_dir_and_only(*, dispatcher: Dispatcher, tmp_dir: Path):
    with given:
        scenarios = [
            make_vscenario(touch(tmp_dir / "scenarios/dir1/scn1.py"), only=True),
            make_vscenario(touch(tmp_dir / "scenarios/dir1/scn2.py")),
            make_vscenario(touch(tmp_dir / "scenarios/scn1.py"), only=True),
        ]

        await fire_arg_parsed_event(dispatcher, file_or_dir=[
            str(tmp_dir / "scenarios/dir1")
        ])

        scheduler = Scheduler(scenarios)
        startup_event = StartupEvent(scheduler)

    with when:
        await dispatcher.fire(startup_event)

    with then:
        assert list(scheduler.scheduled) == [scenarios[0]]
        assert get_skipped(scheduler.scheduled) == []


@pytest.mark.usefixtures(skipper.__name__)
async def test_select_file_and_skip(*, dispatcher: Dispatcher, tmp_dir: Path):
    with given:
        scenarios = [
            make_vscenario(touch(tmp_dir / "scenarios/scn1.py"), skip=True),
            make_vscenario(touch(tmp_dir / "scenarios/scn2.py")),
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
        assert get_skipped(scheduler.scheduled) == [scenarios[0]]


@pytest.mark.usefixtures(skipper.__name__)
async def test_select_dir_and_skip(*, dispatcher: Dispatcher, tmp_dir: Path):
    with given:
        scenarios = [
            make_vscenario(touch(tmp_dir / "scenarios/dir1/scn1.py"), skip=True),
            make_vscenario(touch(tmp_dir / "scenarios/dir1/scn2.py")),
            make_vscenario(touch(tmp_dir / "scenarios/dir2/scn1.py")),
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
        assert get_skipped(scheduler.scheduled) == [scenarios[0]]

# ignore


@pytest.mark.usefixtures(skipper.__name__)
async def test_ignore_file_and_subject(*, dispatcher: Dispatcher, tmp_dir: Path):
    with given:
        subject = "subject"
        scenarios = [
            make_vscenario(touch(tmp_dir / "scenarios/scn1.py"), subject=subject),
            make_vscenario(touch(tmp_dir / "scenarios/scn2.py"), subject=subject),
        ]

        await fire_arg_parsed_event(dispatcher, subject=subject, ignore=[
            str(scenarios[0].path)
        ])

        scheduler = Scheduler(scenarios)
        startup_event = StartupEvent(scheduler)

    with when:
        await dispatcher.fire(startup_event)

    with then:
        assert list(scheduler.scheduled) == [scenarios[1]]
        assert get_skipped(scheduler.scheduled) == []


@pytest.mark.usefixtures(skipper.__name__)
async def test_ignore_dir_and_subject(*, dispatcher: Dispatcher, tmp_dir: Path):
    with given:
        subject = "subject1"
        scenarios = [
            make_vscenario(touch(tmp_dir / "scenarios/dir1/scn1.py"), subject=subject),
            make_vscenario(touch(tmp_dir / "scenarios/dir1/scn2.py"), subject="subject2"),
            make_vscenario(touch(tmp_dir / "scenarios/dir2/scn1.py"), subject=subject),
            make_vscenario(touch(tmp_dir / "scenarios/scn1.py"), subject=subject)
        ]

        await fire_arg_parsed_event(dispatcher, subject=subject, ignore=[
            str(tmp_dir / "scenarios/dir1")
        ])

        scheduler = Scheduler(scenarios)
        startup_event = StartupEvent(scheduler)

    with when:
        await dispatcher.fire(startup_event)

    with then:
        assert list(scheduler.scheduled) == [scenarios[2], scenarios[3]]
        assert get_skipped(scheduler.scheduled) == []


@pytest.mark.usefixtures(skipper.__name__)
async def test_ignore_file_and_only(*, dispatcher: Dispatcher, tmp_dir: Path):
    with given:
        scenarios = [
            make_vscenario(touch(tmp_dir / "scenarios/scn1.py"), only=True),
            make_vscenario(touch(tmp_dir / "scenarios/scn2.py"), only=True),
        ]

        await fire_arg_parsed_event(dispatcher, ignore=[
            str(scenarios[0].path)
        ])

        scheduler = Scheduler(scenarios)
        startup_event = StartupEvent(scheduler)

    with when:
        await dispatcher.fire(startup_event)

    with then:
        assert list(scheduler.scheduled) == [scenarios[1]]
        assert get_skipped(scheduler.scheduled) == []


@pytest.mark.usefixtures(skipper.__name__)
async def test_ignore_dir_and_only(*, dispatcher: Dispatcher, tmp_dir: Path):
    with given:
        scenarios = [
            make_vscenario(touch(tmp_dir / "scenarios/dir1/scn1.py"), only=True),
            make_vscenario(touch(tmp_dir / "scenarios/dir1/scn2.py")),
            make_vscenario(touch(tmp_dir / "scenarios/scn1.py"), only=True),
        ]

        await fire_arg_parsed_event(dispatcher, ignore=[
            str(tmp_dir / "scenarios/dir1")
        ])

        scheduler = Scheduler(scenarios)
        startup_event = StartupEvent(scheduler)

    with when:
        await dispatcher.fire(startup_event)

    with then:
        assert list(scheduler.scheduled) == [scenarios[2]]
        assert get_skipped(scheduler.scheduled) == []


@pytest.mark.usefixtures(skipper.__name__)
async def test_ignore_file_and_skip(*, dispatcher: Dispatcher, tmp_dir: Path):
    with given:
        scenarios = [
            make_vscenario(touch(tmp_dir / "scenarios/scn1.py"), skip=True),
            make_vscenario(touch(tmp_dir / "scenarios/scn2.py"), skip=True),
            make_vscenario(touch(tmp_dir / "scenarios/scn3.py")),
        ]

        await fire_arg_parsed_event(dispatcher, ignore=[
            str(scenarios[0].path)
        ])

        scheduler = Scheduler(scenarios)
        startup_event = StartupEvent(scheduler)

    with when:
        await dispatcher.fire(startup_event)

    with then:
        assert list(scheduler.scheduled) == [scenarios[1], scenarios[2]]
        assert get_skipped(scheduler.scheduled) == [scenarios[1]]


@pytest.mark.usefixtures(skipper.__name__)
async def test_ignore_dir_and_skip(*, dispatcher: Dispatcher, tmp_dir: Path):
    with given:
        scenarios = [
            make_vscenario(touch(tmp_dir / "scenarios/dir1/scn1.py"), skip=True),
            make_vscenario(touch(tmp_dir / "scenarios/dir1/scn2.py")),
            make_vscenario(touch(tmp_dir / "scenarios/dir2/scn1.py"), skip=True),
            make_vscenario(touch(tmp_dir / "scenarios/scn1.py")),
        ]

        await fire_arg_parsed_event(dispatcher, ignore=[
            str(tmp_dir / "scenarios/dir1")
        ])

        scheduler = Scheduler(scenarios)
        startup_event = StartupEvent(scheduler)

    with when:
        await dispatcher.fire(startup_event)

    with then:
        assert list(scheduler.scheduled) == [scenarios[2], scenarios[3]]
        assert get_skipped(scheduler.scheduled) == [scenarios[2]]


# subject


@pytest.mark.usefixtures(skipper.__name__, tmp_dir.__name__)
async def test_subject_and_only(*, dispatcher: Dispatcher):
    with given:
        subject = "subject1"
        scenarios = [
            make_vscenario(subject=subject, only=True),
            make_vscenario(subject=subject),
            make_vscenario(subject="subject2"),
            make_vscenario(subject="subject3", only=True),
        ]

        await fire_arg_parsed_event(dispatcher, subject=subject)

        scheduler = Scheduler(scenarios)
        startup_event = StartupEvent(scheduler)

    with when:
        await dispatcher.fire(startup_event)

    with then:
        assert list(scheduler.scheduled) == [scenarios[0]]
        assert get_skipped(scheduler.scheduled) == []


@pytest.mark.usefixtures(skipper.__name__, tmp_dir.__name__)
async def test_subject_and_skip(*, dispatcher: Dispatcher):
    with given:
        subject = "subject1"
        scenarios = [
            make_vscenario(subject=subject, skip=True),
            make_vscenario(subject=subject),
            make_vscenario(subject="subject2"),
            make_vscenario(subject="subject3", skip=True),
        ]

        await fire_arg_parsed_event(dispatcher, subject=subject)

        scheduler = Scheduler(scenarios)
        startup_event = StartupEvent(scheduler)

    with when:
        await dispatcher.fire(startup_event)

    with then:
        assert list(scheduler.scheduled) == [scenarios[0], scenarios[1]]
        assert get_skipped(scheduler.scheduled) == [scenarios[0]]


# @only & @skip

@pytest.mark.usefixtures(skipper.__name__, tmp_dir.__name__)
async def test_only_and_skip(*, dispatcher: Dispatcher):
    with given:
        scenarios = [
            make_vscenario(only=True),
            make_vscenario(skip=True),
            make_vscenario(only=True, skip=True),
        ]

        await fire_arg_parsed_event(dispatcher)

        scheduler = Scheduler(scenarios)
        startup_event = StartupEvent(scheduler)

    with when:
        await dispatcher.fire(startup_event)

    with then:
        assert list(scheduler.scheduled) == [scenarios[0], scenarios[2]]
        assert get_skipped(scheduler.scheduled) == [scenarios[2]]
