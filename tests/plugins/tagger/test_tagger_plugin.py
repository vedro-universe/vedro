import pytest
from baby_steps import given, then, when
from pytest import raises

from vedro.core import Dispatcher
from vedro.core import MonotonicScenarioScheduler as Scheduler
from vedro.events import StartupEvent

from ._utils import dispatcher, fire_arg_parsed_event, make_vscenario, tagger

__all__ = ("dispatcher", "tagger")  # fixtures


@pytest.mark.usefixtures(tagger.__name__)
async def test_no_tags(*, dispatcher: Dispatcher):
    with given:
        await fire_arg_parsed_event(dispatcher, tags=None)

        scenarios = [make_vscenario(), make_vscenario()]
        scheduler = Scheduler(scenarios)
        startup_event = StartupEvent(scheduler)

    with when:
        await dispatcher.fire(startup_event)

    with then:
        assert list(scheduler.scheduled) == scenarios


@pytest.mark.usefixtures(tagger.__name__)
async def test_nonexisting_tag(*, dispatcher: Dispatcher):
    with given:
        await fire_arg_parsed_event(dispatcher, tags="SMOKE")

        scenarios = [make_vscenario(), make_vscenario()]
        scheduler = Scheduler(scenarios)
        startup_event = StartupEvent(scheduler)

    with when:
        await dispatcher.fire(startup_event)

    with then:
        assert list(scheduler.scheduled) == []


@pytest.mark.usefixtures(tagger.__name__)
async def test_tag(*, dispatcher: Dispatcher):
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


@pytest.mark.usefixtures(tagger.__name__)
async def test_tag_not_operator(*, dispatcher: Dispatcher):
    with given:
        await fire_arg_parsed_event(dispatcher, tags="not SMOKE")

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
        assert list(scheduler.scheduled) == [scenarios[1]]


@pytest.mark.usefixtures(tagger.__name__)
async def test_tag_and_operator(*, dispatcher: Dispatcher):
    with given:
        await fire_arg_parsed_event(dispatcher, tags="SMOKE and P0")

        scenarios = [
            make_vscenario(tags=["SMOKE"]),
            make_vscenario(),
            make_vscenario(tags=["SMOKE", "P0"]),
            make_vscenario(tags=["P0"])
        ]
        scheduler = Scheduler(scenarios)
        startup_event = StartupEvent(scheduler)

    with when:
        await dispatcher.fire(startup_event)

    with then:
        assert list(scheduler.scheduled) == [scenarios[2]]


@pytest.mark.usefixtures(tagger.__name__)
async def test_tag_and_operators(*, dispatcher: Dispatcher):
    with given:
        await fire_arg_parsed_event(dispatcher, tags="SMOKE and P0 and API")

        scenarios = [
            make_vscenario(tags=["SMOKE"]),
            make_vscenario(tags=["SMOKE", "P0"]),
            make_vscenario(tags=["P0", "API"]),
            make_vscenario(tags=["SMOKE", "API"]),
            make_vscenario(tags=["SMOKE", "P0", "API"]),
            make_vscenario(tags=["API"]),
            make_vscenario(),
        ]
        scheduler = Scheduler(scenarios)
        startup_event = StartupEvent(scheduler)

    with when:
        await dispatcher.fire(startup_event)

    with then:
        assert list(scheduler.scheduled) == [scenarios[4]]


@pytest.mark.usefixtures(tagger.__name__)
async def test_tag_or_operator(*, dispatcher: Dispatcher):
    with given:
        await fire_arg_parsed_event(dispatcher, tags="SMOKE or P0")

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


@pytest.mark.usefixtures(tagger.__name__)
async def test_tag_or_operators(*, dispatcher: Dispatcher):
    with given:
        await fire_arg_parsed_event(dispatcher, tags="SMOKE or P0 or API")

        scenarios = [
            make_vscenario(),
            make_vscenario(tags=["SMOKE"]),
            make_vscenario(tags=["P0"]),
            make_vscenario(tags=["SMOKE", "P0"]),
            make_vscenario(tags=["API"]),
            make_vscenario(tags=["SMOKE", "P0", "API"]),
        ]
        scheduler = Scheduler(scenarios)
        startup_event = StartupEvent(scheduler)

    with when:
        await dispatcher.fire(startup_event)

    with then:
        assert list(scheduler.scheduled) == scenarios[1:]


@pytest.mark.usefixtures(tagger.__name__)
async def test_tags_expr(*, dispatcher: Dispatcher):
    with given:
        await fire_arg_parsed_event(dispatcher, tags="(not SMOKE) and (not P0)")

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
        assert list(scheduler.scheduled) == [scenarios[1]]


@pytest.mark.usefixtures(tagger.__name__)
async def test_tags_skipped(*, dispatcher: Dispatcher):
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


@pytest.mark.usefixtures(tagger.__name__)
async def test_tags_type_validation(*, dispatcher: Dispatcher):
    with given:
        await fire_arg_parsed_event(dispatcher, tags="SMOKE")

        scenario = make_vscenario(tags={"SMOKE": "SMOKE"})  # type: ignore
        scheduler = Scheduler([scenario])

        startup_event = StartupEvent(scheduler)

    with when, raises(BaseException) as exc:
        await dispatcher.fire(startup_event)

    with then:
        assert exc.type is TypeError
        assert str(exc.value) == (f"Scenario '{scenario.unique_id}' tags must be a list, "
                                  "tuple or set, got <class 'dict'>")


@pytest.mark.usefixtures(tagger.__name__)
async def test_tags_value_validation(*, dispatcher: Dispatcher):
    with given:
        await fire_arg_parsed_event(dispatcher, tags="SMOKE")

        scenario = make_vscenario(tags=["-SMOKE"])
        scheduler = Scheduler([scenario])

        startup_event = StartupEvent(scheduler)

    with when, raises(BaseException) as exc:
        await dispatcher.fire(startup_event)

    with then:
        assert exc.type is ValueError
        assert str(exc.value).startswith(
            f"Scenario '{scenario.unique_id}' tag '-SMOKE' is not valid"
        )


@pytest.mark.usefixtures(tagger.__name__)
async def test_tags_tag_type_validation(*, dispatcher: Dispatcher):
    with given:
        await fire_arg_parsed_event(dispatcher, tags="SMOKE")

        scenario = make_vscenario(tags=[None])  # type: ignore
        scheduler = Scheduler([scenario])

        startup_event = StartupEvent(scheduler)

    with when, raises(BaseException) as exc:
        await dispatcher.fire(startup_event)

    with then:
        assert exc.type is ValueError
        assert str(exc.value).startswith(
            f"Scenario '{scenario.unique_id}' tag 'None' is not valid"
        )
