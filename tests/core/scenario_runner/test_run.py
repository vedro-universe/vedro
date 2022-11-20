from unittest.mock import Mock

import pytest
from baby_steps import given, then, when

from vedro.core import ExcInfo, MonotonicScenarioRunner
from vedro.core import MonotonicScenarioScheduler as Scheduler
from vedro.core import Report

from ._utils import dispatcher_, make_vscenario, make_vstep, runner

__all__ = ("dispatcher_", "runner")  # fixtures


@pytest.mark.asyncio
async def test_run_no_scenarios(*, runner: MonotonicScenarioRunner, dispatcher_: Mock):
    with given:
        scheduler = Scheduler([])

    with when:
        report = await runner.run(scheduler)

    with then:
        assert isinstance(report, Report)
        assert report.total == 0
        assert report.interrupted is None


@pytest.mark.asyncio
async def test_run_scenario(*, runner: MonotonicScenarioRunner, dispatcher_: Mock):
    with given:
        vscenario = make_vscenario(steps=[])
        scheduler = Scheduler([vscenario])

    with when:
        report = await runner.run(scheduler)

    with then:
        assert isinstance(report, Report)
        assert report.total == 1
        assert report.interrupted is None


@pytest.mark.asyncio
async def test_run_step_interrupted(*, runner: MonotonicScenarioRunner, dispatcher_: Mock):
    with given:
        interrupt_exception = KeyboardInterrupt
        step_ = Mock(side_effect=interrupt_exception())
        vscenario = make_vscenario(steps=[make_vstep(step_)])

        scheduler = Scheduler([vscenario])
        runner = MonotonicScenarioRunner(dispatcher_, interrupt_exceptions=(interrupt_exception,))

    with when:
        report = await runner.run(scheduler)

    with then:
        assert isinstance(report, Report)
        assert report.total == 1
        assert report.failed == 1

        assert isinstance(report.interrupted, ExcInfo)
        assert isinstance(report.interrupted.value, interrupt_exception)


@pytest.mark.asyncio
async def test_run_scenario_interrupted(*, runner: MonotonicScenarioRunner, dispatcher_: Mock):
    with given:
        interrupt_exception = KeyboardInterrupt
        vscenario = make_vscenario()

        scheduler = Scheduler([vscenario])
        scheduler.aggregate_results = Mock(side_effect=interrupt_exception())

        runner = MonotonicScenarioRunner(dispatcher_, interrupt_exceptions=(interrupt_exception,))

    with when:
        report = await runner.run(scheduler)

    with then:
        assert isinstance(report, Report)
        assert report.total == 0

        assert isinstance(report.interrupted, ExcInfo)
        assert isinstance(report.interrupted.value, interrupt_exception)
