from typing import Type, cast
from unittest.mock import Mock, call

import pytest
from baby_steps import given, then, when
from pytest import raises

from vedro.core import Event, MonotonicScenarioRunner
from vedro.core import MonotonicScenarioScheduler as Scheduler
from vedro.core import Report
from vedro.core._scenario_runner import RunInterrupted
from vedro.events import ScenarioPassedEvent, ScenarioReportedEvent, ScenarioRunEvent

from ._utils import (
    dispatcher_,
    interrupt_exception,
    make_aggregated_result,
    make_vscenario,
    make_vstep,
    runner,
)

__all__ = ("dispatcher_", "runner", "interrupt_exception",)  # fixtures


@pytest.mark.asyncio
async def test_run_no_scenarios(*, runner: MonotonicScenarioRunner, dispatcher_: Mock):
    with given:
        report = Report()
        scheduler = Scheduler([])

    with when:
        await runner._run_scenarios(scheduler, report)

    with then:
        assert report.total == 0
        assert report.interrupted is None

        assert dispatcher_.mock_calls == []


@pytest.mark.asyncio
async def test_run_scenario(*, runner: MonotonicScenarioRunner, dispatcher_: Mock):
    with given:
        report = Report()
        vscenario = make_vscenario()
        scheduler = Scheduler([vscenario])

        aggregate_result = make_aggregated_result()
        scheduler.aggregate_results = Mock(return_value=aggregate_result)

    with when:
        await runner._run_scenarios(scheduler, report)

    with then:
        assert report.total == 1
        assert report.interrupted is None

        scenario_results = scheduler.aggregate_results.mock_calls[0].args[0]
        assert len(scenario_results) == 1

        assert dispatcher_.mock_calls == [
            call.fire(ScenarioRunEvent(scenario_results[0])),
            call.fire(ScenarioPassedEvent(scenario_results[0])),
            call.fire(ScenarioReportedEvent(aggregate_result)),
        ]


@pytest.mark.asyncio
async def test_run_scenarios(*, runner: MonotonicScenarioRunner, dispatcher_: Mock):
    with given:
        report = Report()
        vscenario = make_vscenario()
        scheduler = Scheduler([vscenario])

        new_vscenario = make_vscenario()
        for _ in range(2):
            scheduler.schedule(new_vscenario)

        first_aggregate_result = make_aggregated_result()
        second_aggregate_result = make_aggregated_result()
        scheduler.aggregate_results = Mock(side_effect=(first_aggregate_result,
                                                        second_aggregate_result))

    with when:
        await runner._run_scenarios(scheduler, report)

    with then:
        assert report.total == 2
        assert report.interrupted is None

        # new_vscenario was scheduled twice
        new_scenario_results = scheduler.aggregate_results.mock_calls[0].args[0]
        assert len(new_scenario_results) == 2

        # vscenario was scheduled once
        scenario_results = scheduler.aggregate_results.mock_calls[1].args[0]
        assert len(scenario_results) == 1

        assert dispatcher_.mock_calls == [
            call.fire(ScenarioRunEvent(new_scenario_results[0])),
            call.fire(ScenarioPassedEvent(new_scenario_results[0])),
            call.fire(ScenarioRunEvent(new_scenario_results[1])),
            call.fire(ScenarioPassedEvent(new_scenario_results[1])),
            call.fire(ScenarioReportedEvent(first_aggregate_result)),

            call.fire(ScenarioRunEvent(scenario_results[0])),
            call.fire(ScenarioPassedEvent(scenario_results[0])),
            call.fire(ScenarioReportedEvent(second_aggregate_result)),
        ]


@pytest.mark.asyncio
async def test_step_interrupted(*, runner: MonotonicScenarioRunner,
                                interrupt_exception: Type[BaseException], dispatcher_: Mock):
    with given:
        vstep = make_vstep(Mock(side_effect=interrupt_exception()))
        vscenario = make_vscenario(steps=[vstep])

        report = Report()
        scheduler = Scheduler([vscenario])
        aggregate_result = make_aggregated_result().mark_failed()
        scheduler.aggregate_results = Mock(return_value=aggregate_result)

    with when, raises(BaseException) as exc:
        await runner._run_scenarios(scheduler, report)

    with then:
        assert report.total == 1
        assert report.failed == 1

        assert exc.type is RunInterrupted
        orig_exc = cast(RunInterrupted, exc.value)
        assert isinstance(orig_exc.exc_info.value, interrupt_exception)

        scenario_results = scheduler.aggregate_results.mock_calls[0].args[0]
        assert scenario_results[0].is_failed()
        assert len(scenario_results) == 1

        assert dispatcher_.mock_calls[-1] == call.fire(ScenarioReportedEvent(aggregate_result))


@pytest.mark.asyncio
async def test_scenario_interrupted(*, runner: MonotonicScenarioRunner,
                                    interrupt_exception: Type[BaseException], dispatcher_: Mock):
    with given:
        vscenario = make_vscenario()
        scheduler = Scheduler([vscenario])
        report = Report()

        async def fire(event: Event):
            if isinstance(event, ScenarioPassedEvent):
                raise interrupt_exception()
        dispatcher_.fire = fire

    with when, raises(BaseException) as exc:
        await runner._run_scenarios(scheduler, report)

    with then:
        assert report.total == 0

        assert exc.type is RunInterrupted
        orig_exc = cast(RunInterrupted, exc.value)
        assert isinstance(orig_exc.exc_info.value, interrupt_exception)
