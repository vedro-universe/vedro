import pytest
from baby_steps import given, then, when
from pytest import raises

from vedro.core import Dispatcher
from vedro.core import MonotonicScenarioScheduler as Scheduler
from vedro.events import StartupEvent
from vedro.plugins.tagger import TaggerPlugin

from ._utils import dispatcher, fire_arg_parsed_event, make_vscenario, tagger

__all__ = ("dispatcher", "tagger")  # fixtures


@pytest.mark.asyncio
@pytest.mark.usefixtures(tagger.__name__)
async def test_no_tags(*, tagger: TaggerPlugin, dispatcher: Dispatcher):
    with given:
        await fire_arg_parsed_event(dispatcher, tags=None)

        scenarios = [make_vscenario(), make_vscenario()]
        scheduler = Scheduler(scenarios)
        startup_event = StartupEvent(scheduler)

    with when:
        await dispatcher.fire(startup_event)

    with then:
        assert list(scheduler.scheduled) == scenarios


@pytest.mark.asyncio
async def test_nonexisting_tag(*, tagger: TaggerPlugin, dispatcher: Dispatcher):
    with given:
        await fire_arg_parsed_event(dispatcher, tags="SMOKE")

        scenarios = [make_vscenario(), make_vscenario()]
        scheduler = Scheduler(scenarios)

        startup_event = StartupEvent(scheduler)

    with when:
        await dispatcher.fire(startup_event)

    with then:
        assert list(scheduler.scheduled) == []


@pytest.mark.asyncio
async def test_tags(*, tagger: TaggerPlugin, dispatcher: Dispatcher):
    with given:
        await fire_arg_parsed_event(dispatcher, tags="SMOKE")

        scenarios = [
            make_vscenario(tags=["SMOKE"]),
            make_vscenario(),
            make_vscenario(tags=["SMOKE", "P0"])
        ]
        scheduler = Scheduler(scenarios)

        startup_event = StartupEvent(scheduler)

    with when:
        await dispatcher.fire(startup_event)

    with then:
        assert list(scheduler.scheduled) == [scenarios[0], scenarios[2]]


@pytest.mark.asyncio
async def test_tags_skipped(*, tagger: TaggerPlugin, dispatcher: Dispatcher):
    with given:
        await fire_arg_parsed_event(dispatcher, tags="SMOKE")

        scenarios = [
            make_vscenario(tags=["SMOKE"], is_skipped=True),
            make_vscenario(is_skipped=True),
            make_vscenario(),
        ]
        scheduler = Scheduler(scenarios)

        startup_event = StartupEvent(scheduler)

    with when:
        await dispatcher.fire(startup_event)

    with then:
        assert list(scheduler.scheduled) == [scenarios[0]]


@pytest.mark.asyncio
async def test_tags_type_validation(*, tagger: TaggerPlugin, dispatcher: Dispatcher):
    with given:
        await fire_arg_parsed_event(dispatcher, tags="SMOKE")

        scenario = make_vscenario(tags="SMOKE")
        scheduler = Scheduler([scenario])

        startup_event = StartupEvent(scheduler)

    with when, raises(BaseException) as exc:
        await dispatcher.fire(startup_event)

    with then:
        assert exc.type is TypeError
        assert str(exc.value) == (
            f"Scenario '{scenario.rel_path}' tags must be a list, tuple or set, got <class 'str'>"
        )


@pytest.mark.asyncio
async def test_tags_value_validation(*, tagger: TaggerPlugin, dispatcher: Dispatcher):
    with given:
        await fire_arg_parsed_event(dispatcher, tags="SMOKE")

        scenario = make_vscenario(tags=["-SMOKE"])
        scheduler = Scheduler([scenario])

        startup_event = StartupEvent(scheduler)

    with when, raises(BaseException) as exc:
        await dispatcher.fire(startup_event)

    with then:
        assert exc.type is ValueError
        assert str(exc.value) == (
            f"Scenario '{scenario.rel_path}' tag '-SMOKE' is not a valid identifier"
        )
