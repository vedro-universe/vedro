import sys
from time import time
from typing import List, Tuple, Type

from ..._scenario import Scenario
from ...events import (
    ExceptionRaisedEvent,
    ScenarioFailedEvent,
    ScenarioPassedEvent,
    ScenarioReportedEvent,
    ScenarioRunEvent,
    ScenarioSkippedEvent,
    StepFailedEvent,
    StepPassedEvent,
    StepRunEvent,
)
from .._dispatcher import Dispatcher
from .._exc_info import ExcInfo
from .._report import Report
from .._scenario_result import ScenarioResult
from .._scenario_scheduler import ScenarioScheduler
from .._step_result import StepResult
from .._virtual_scenario import VirtualScenario
from .._virtual_step import VirtualStep
from ._scenario_runner import ScenarioRunner

__all__ = ("MonotonicScenarioRunner",)


class _ScenarioInitError(Exception):
    pass


class MonotonicScenarioRunner(ScenarioRunner):
    def __init__(self, dispatcher: Dispatcher,
                 interrupt_exceptions: Tuple[Type[BaseException], ...] = ()) -> None:
        self._dispatcher = dispatcher
        self._interrupt_exceptions = interrupt_exceptions

    async def run_step(self, step: VirtualStep, ref: Scenario) -> StepResult:
        step_result = StepResult(step)

        await self._dispatcher.fire(StepRunEvent(step_result))
        step_result.set_started_at(time())
        try:
            if step.is_coro():
                await step(ref)
            else:
                step(ref)
        except:  # noqa: E722
            step_result.set_ended_at(time())

            exc_info = ExcInfo(*sys.exc_info())
            await self._dispatcher.fire(ExceptionRaisedEvent(exc_info))
            step_result.set_exc_info(exc_info)

            step_result.mark_failed()
            await self._dispatcher.fire(StepFailedEvent(step_result))

            if exc_info.type in self._interrupt_exceptions:
                raise exc_info.value
        else:
            step_result.set_ended_at(time())
            step_result.mark_passed()
            await self._dispatcher.fire(StepPassedEvent(step_result))

        return step_result

    async def run_scenario(self, scenario: VirtualScenario) -> ScenarioResult:
        scenario_result = ScenarioResult(scenario)
        try:
            ref = scenario()
        except Exception as exc:
            message = (f'Can\'t initialize scenario "{scenario_result.scenario.subject}" '
                       f'at "{scenario_result.scenario.rel_path}" ({exc})')
            raise _ScenarioInitError(message) from None
        scenario_result.set_scope(ref.__dict__)

        if scenario.is_skipped():
            scenario_result.mark_skipped()
            await self._dispatcher.fire(ScenarioSkippedEvent(scenario_result))
            return scenario_result

        await self._dispatcher.fire(ScenarioRunEvent(scenario_result))
        scenario_result.set_started_at(time())
        for step in scenario.steps:
            step_result = await self.run_step(step, ref)
            scenario_result.add_step_result(step_result)

            if step_result.is_failed():
                scenario_result.set_ended_at(time())
                scenario_result.mark_failed()
                await self._dispatcher.fire(ScenarioFailedEvent(scenario_result))
                break

        if not scenario_result.is_failed():
            scenario_result.set_ended_at(time())
            scenario_result.mark_passed()
            await self._dispatcher.fire(ScenarioPassedEvent(scenario_result))

        return scenario_result

    async def run(self, scheduler: ScenarioScheduler) -> Report:
        report = Report()
        scenario_results: List[ScenarioResult] = []

        async for scenario in scheduler:
            if len(scenario_results) > 0 and \
               scenario_results[-1].scenario.unique_id != scenario.unique_id:
                aggregated_result = scheduler.aggregate_results(scenario_results)
                report.add_result(aggregated_result)
                await self._dispatcher.fire(ScenarioReportedEvent(aggregated_result))
                scenario_results = []

            scenario_result = await self.run_scenario(scenario)
            scenario_results.append(scenario_result)

        if len(scenario_results) > 0:
            aggregated_result = scheduler.aggregate_results(scenario_results)
            report.add_result(aggregated_result)
            await self._dispatcher.fire(ScenarioReportedEvent(aggregated_result))

        return report
