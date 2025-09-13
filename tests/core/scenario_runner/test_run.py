from typing import Type
from unittest.mock import Mock

from baby_steps import given, then, when

from vedro.core import ExcInfo, MonotonicScenarioRunner
from vedro.core import MonotonicScenarioScheduler as Scheduler
from vedro.core import Report

from ._utils import (
    dispatcher_,
    interrupt_exception,
    make_vscenario,
    make_vstep,
    runner,
    step_recorder,
)

__all__ = ("dispatcher_", "runner", "interrupt_exception", "step_recorder",)  # fixtures


async def test_run_no_scenarios(*, runner: MonotonicScenarioRunner, dispatcher_: Mock):
    with given:
        scheduler = Scheduler([])

    with when:
        report = await runner.run(scheduler)

    with then:
        assert isinstance(report, Report)
        assert report.total == 0
        assert report.interrupted is None


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


async def test_run_step_interrupted(*, runner: MonotonicScenarioRunner,
                                    interrupt_exception: Type[BaseException], dispatcher_: Mock):
    with given:
        step_ = Mock(side_effect=interrupt_exception())
        vscenario = make_vscenario(steps=[make_vstep(step_)])
        scheduler = Scheduler([vscenario])

    with when:
        report = await runner.run(scheduler)

    with then:
        assert isinstance(report, Report)
        assert report.total == 1
        assert report.failed == 1

        assert isinstance(report.interrupted, ExcInfo)
        assert isinstance(report.interrupted.value, interrupt_exception)


async def test_run_scenario_interrupted(*, runner: MonotonicScenarioRunner,
                                        interrupt_exception: Type[BaseException],
                                        dispatcher_: Mock):
    with given:
        vscenario = make_vscenario()
        scheduler = Scheduler([vscenario])
        scheduler.aggregate_results = Mock(side_effect=interrupt_exception())

    with when:
        report = await runner.run(scheduler)

    with then:
        assert isinstance(report, Report)
        assert report.total == 0

        assert isinstance(report.interrupted, ExcInfo)
        assert isinstance(report.interrupted.value, interrupt_exception)
