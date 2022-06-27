import pytest
from baby_steps import given, then, when

from vedro.core import Dispatcher
from vedro.core import MonotonicScenarioScheduler as Scheduler
from vedro.events import StartupEvent
from vedro.plugins.tagger import TaggerPlugin

from ._utils import dispatcher, fire_arg_parsed_event, make_virtual_scenario, tagger

__all__ = ("dispatcher", "tagger",)  # fixtures


@pytest.mark.asyncio
async def test_no_tags(*, tagger: TaggerPlugin, dispatcher: Dispatcher):
    with given:
        await fire_arg_parsed_event(dispatcher, tags=None)

        scenarios = [make_virtual_scenario(), make_virtual_scenario()]
        scheduler = Scheduler(scenarios)
        startup_event = StartupEvent(scheduler)

    with when:
        await dispatcher.fire(startup_event)

    with then:
        assert list(scheduler.scheduled) == scenarios


@pytest.mark.asyncio
async def test_nonexisting_tag(*, tagger: TaggerPlugin, dispatcher: Dispatcher):
    with given:
        await fire_arg_parsed_event(dispatcher, tags="API")

        scenarios = [make_virtual_scenario(), make_virtual_scenario()]
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
            make_virtual_scenario(tags=["SMOKE"]),
            make_virtual_scenario(),
            make_virtual_scenario(tags=["SMOKE", "P0"])
        ]
        scheduler = Scheduler(scenarios)

        startup_event = StartupEvent(scheduler)

    with when:
        await dispatcher.fire(startup_event)

    with then:
        assert list(scheduler.scheduled) == [scenarios[0], scenarios[2]]
