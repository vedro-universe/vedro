import sys
from unittest.mock import Mock, call

import pytest
from baby_steps import given, then, when

from vedro.core import MonotonicScenarioScheduler as Scheduler
from vedro.core import Report
from vedro.events import (
    ScenarioPassedEvent,
    ScenarioReportedEvent,
    ScenarioRunEvent,
    ScenarioSkippedEvent,
    StepPassedEvent,
    StepRunEvent,
)
from vedro.plugins.dry_runner import DryRunnerImpl

from ._utils import (
    dispatcher_,
    dry_runner,
    interrupt_exception,
    make_aggregated_result,
    make_vscenario,
    make_vstep,
)

__all__ = ("dispatcher_", "dry_runner", "interrupt_exception",)  # fixtures


@pytest.mark.asyncio
async def test_run_step(*, dry_runner: DryRunnerImpl, dispatcher_: Mock):
    with given:
        step_ = Mock()
        vstep = make_vstep(step_)

    with when:
        step_result = await dry_runner.run_step(vstep)

    with then:
        assert step_result.is_passed() is True
        assert isinstance(step_result.started_at, float)
        assert isinstance(step_result.ended_at, float)

        assert step_.mock_calls == []

        assert dispatcher_.mock_calls == [
            call.fire(StepRunEvent(step_result)),
            call.fire(StepPassedEvent(step_result)),
        ]


@pytest.mark.asyncio
async def test_run_passed_scenario(*, dry_runner: DryRunnerImpl, dispatcher_: Mock):
    with given:
        step1_, step2_ = Mock(), Mock()
        vstep1, vstep2 = make_vstep(step1_), make_vstep(step2_)
        vscenario = make_vscenario(steps=[vstep1, vstep2])

    with when:
        scenario_result = await dry_runner.run_scenario(vscenario)

    with then:
        assert scenario_result.is_passed() is True
        assert isinstance(scenario_result.started_at, float)
        assert isinstance(scenario_result.ended_at, float)

        assert step1_.mock_calls == step2_.mock_calls == []

        step1_result, step2_result = scenario_result.step_results
        assert dispatcher_.mock_calls == [
            call.fire(ScenarioRunEvent(scenario_result)),

            call.fire(StepRunEvent(step1_result)),
            call.fire(StepPassedEvent(step1_result)),

            call.fire(StepRunEvent(step2_result)),
            call.fire(StepPassedEvent(step2_result)),

            call.fire(ScenarioPassedEvent(scenario_result)),
        ]


@pytest.mark.asyncio
async def test_run_skipped_scenario(*, dry_runner: DryRunnerImpl, dispatcher_: Mock):
    with given:
        step_ = Mock()
        vstep = make_vstep(step_)
        vscenario = make_vscenario(steps=[vstep], is_skipped=True)

    with when:
        scenario_result = await dry_runner.run_scenario(vscenario)

    with then:
        assert scenario_result.is_skipped() is True
        assert scenario_result.started_at is None
        assert scenario_result.ended_at is None

        assert step_.mock_calls == []

        assert dispatcher_.mock_calls == [
            call.fire(ScenarioSkippedEvent(scenario_result)),
        ]


@pytest.mark.asyncio
async def test_run_no_scenarios(*, dry_runner: DryRunnerImpl, dispatcher_: Mock):
    with given:
        scheduler = Scheduler([])

    with when:
        report = await dry_runner.run(scheduler)

    with then:
        assert isinstance(report, Report)
        assert report.total == 0

        assert dispatcher_.mock_calls == []


@pytest.mark.asyncio
@pytest.mark.skipif(sys.version_info < (3, 8), reason="call.args returns call")
async def test_run_scenario(*, dry_runner: DryRunnerImpl, dispatcher_: Mock):
    with given:
        vscenario = make_vscenario()
        scheduler = Scheduler([vscenario])

        aggregate_result = make_aggregated_result().mark_passed()
        scheduler.aggregate_results = Mock(return_value=aggregate_result)

    with when:
        report = await dry_runner.run(scheduler)

    with then:
        assert isinstance(report, Report)
        assert report.total == 1
        assert report.passed == 1

        scenario_results = scheduler.aggregate_results.mock_calls[0].args[0]
        assert len(scenario_results) == 1

        assert dispatcher_.mock_calls == [
            call.fire(ScenarioRunEvent(scenario_results[0])),
            call.fire(ScenarioPassedEvent(scenario_results[0])),
            call.fire(ScenarioReportedEvent(aggregate_result)),
        ]


@pytest.mark.asyncio
@pytest.mark.skipif(sys.version_info < (3, 8), reason="call.args returns call")
async def test_run_scenarios(*, dry_runner: DryRunnerImpl, dispatcher_: Mock):
    with given:
        vscenario = make_vscenario()
        scheduler = Scheduler([vscenario])

        new_vscenario = make_vscenario()
        for _ in range(2):
            scheduler.schedule(new_vscenario)

        first_aggregate_result = make_aggregated_result().mark_passed()
        second_aggregate_result = make_aggregated_result().mark_passed()
        scheduler.aggregate_results = Mock(side_effect=(first_aggregate_result,
                                                        second_aggregate_result))

    with when:
        report = await dry_runner.run(scheduler)

    with then:
        assert isinstance(report, Report)
        assert report.total == 2
        assert report.passed == 2

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
