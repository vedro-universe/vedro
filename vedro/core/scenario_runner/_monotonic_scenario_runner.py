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
from .._step_result import StepResult
from .._virtual_scenario import VirtualScenario
from .._virtual_step import VirtualStep
from ..scenario_scheduler import ScenarioScheduler
from ._interrupted import Interrupted, RunInterrupted, ScenarioInterrupted, StepInterrupted
from ._scenario_runner import ScenarioRunner

__all__ = ("MonotonicScenarioRunner",)


class MonotonicScenarioRunner(ScenarioRunner):
    def __init__(self, dispatcher: Dispatcher, *,
                 interrupt_exceptions: Tuple[Type[BaseException], ...] = ()) -> None:
        self._dispatcher = dispatcher
        assert isinstance(interrupt_exceptions, tuple)
        self._interrupt_exceptions = interrupt_exceptions + (Interrupted,)

    def _is_interruption(self, exc_info: ExcInfo,
                         exceptions: Tuple[Type[BaseException], ...]) -> bool:
        for exception in exceptions:
            if isinstance(exc_info.value, exception):
                return True
        return False

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
            step_result.set_ended_at(time()).mark_failed()

            exc_info = ExcInfo(*sys.exc_info())
            await self._dispatcher.fire(ExceptionRaisedEvent(exc_info))
            step_result.set_exc_info(exc_info)

            await self._dispatcher.fire(StepFailedEvent(step_result))

            if self._is_interruption(exc_info, self._interrupt_exceptions):
                raise StepInterrupted(exc_info, step_result)
        else:
            step_result.set_ended_at(time()).mark_passed()
            await self._dispatcher.fire(StepPassedEvent(step_result))

        return step_result

    async def run_scenario(self, scenario: VirtualScenario) -> ScenarioResult:
        scenario_result = ScenarioResult(scenario)
        ref = scenario()
        scenario_result.set_scope(ref.__dict__)

        if scenario.is_skipped():
            scenario_result.mark_skipped()
            await self._dispatcher.fire(ScenarioSkippedEvent(scenario_result))
            return scenario_result

        await self._dispatcher.fire(ScenarioRunEvent(scenario_result))
        scenario_result.set_started_at(time())
        for step in scenario.steps:
            try:
                step_result = await self.run_step(step, ref)
            except self._interrupt_exceptions as e:
                if isinstance(e, StepInterrupted):
                    scenario_result.add_step_result(e.step_result)
                    exc_info = e.exc_info
                else:
                    exc_info = ExcInfo(*sys.exc_info())
                scenario_result.set_ended_at(time()).mark_failed()
                await self._dispatcher.fire(ScenarioFailedEvent(scenario_result))
                raise ScenarioInterrupted(exc_info, scenario_result)
            else:
                scenario_result.add_step_result(step_result)

            if step_result.is_failed():
                scenario_result.set_ended_at(time()).mark_failed()
                await self._dispatcher.fire(ScenarioFailedEvent(scenario_result))
                break

        if not scenario_result.is_failed():
            scenario_result.set_ended_at(time()).mark_passed()
            await self._dispatcher.fire(ScenarioPassedEvent(scenario_result))

        return scenario_result

    async def _report_scenario_results(self, scenario_results: List[ScenarioResult],
                                       report: Report, scheduler: ScenarioScheduler) -> None:
        aggregated_result = scheduler.aggregate_results(scenario_results)
        report.add_result(aggregated_result)
        await self._dispatcher.fire(ScenarioReportedEvent(aggregated_result))

    async def _run_scenarios(self, scheduler: ScenarioScheduler, report: Report) -> None:
        scenario_results: List[ScenarioResult] = []

        async for scenario in scheduler:
            prev_scenario = scenario_results[-1].scenario if len(scenario_results) > 0 else None
            if prev_scenario and prev_scenario.unique_id != scenario.unique_id:
                await self._report_scenario_results(scenario_results, report, scheduler)
                scenario_results = []

            try:
                scenario_result = await self.run_scenario(scenario)
            except self._interrupt_exceptions as e:
                if isinstance(e, ScenarioInterrupted):
                    scenario_results.append(e.scenario_result)
                    exc_info = e.exc_info
                else:
                    exc_info = ExcInfo(*sys.exc_info())
                if len(scenario_results) > 0:
                    await self._report_scenario_results(scenario_results, report, scheduler)
                raise RunInterrupted(exc_info)
            else:
                scenario_results.append(scenario_result)

        if len(scenario_results) > 0:
            await self._report_scenario_results(scenario_results, report, scheduler)

    async def run(self, scheduler: ScenarioScheduler) -> Report:
        report = Report()
        try:
            await self._run_scenarios(scheduler, report)
        except self._interrupt_exceptions as e:
            exc_info = e.exc_info if isinstance(e, RunInterrupted) else ExcInfo(*sys.exc_info())
            report.set_interrupted(exc_info)
        return report
