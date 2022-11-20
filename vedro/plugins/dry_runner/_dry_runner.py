import sys
from time import time
from typing import List, Tuple, Type

from vedro.core import (
    Dispatcher,
    ExcInfo,
    Report,
    ScenarioResult,
    ScenarioScheduler,
    StepResult,
    VirtualScenario,
    VirtualStep,
)
from vedro.core.scenario_runner import Interrupted, ScenarioRunner
from vedro.events import (
    ScenarioFailedEvent,
    ScenarioPassedEvent,
    ScenarioReportedEvent,
    ScenarioRunEvent,
    ScenarioSkippedEvent,
    StepPassedEvent,
    StepRunEvent,
)

__all__ = ("DryRunner",)


class DryRunner(ScenarioRunner):
    def __init__(self, dispatcher: Dispatcher, *,
                 interrupt_exceptions: Tuple[Type[BaseException], ...] = ()) -> None:
        self._dispatcher = dispatcher
        assert isinstance(interrupt_exceptions, tuple)
        self._interrupt_exceptions = interrupt_exceptions + (Interrupted,)

    async def run_step(self, step: VirtualStep) -> StepResult:
        step_result = StepResult(step)

        await self._dispatcher.fire(StepRunEvent(step_result))
        step_result.set_started_at(time()).set_ended_at(time())
        step_result.mark_passed()
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
            step_result = await self.run_step(step)
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

            scenario_result = await self.run_scenario(scenario)
            scenario_results.append(scenario_result)

        if len(scenario_results) > 0:
            await self._report_scenario_results(scenario_results, report, scheduler)

    async def run(self, scheduler: ScenarioScheduler) -> Report:
        report = Report()
        try:
            await self._run_scenarios(scheduler, report)
        except self._interrupt_exceptions:
            exc_info = ExcInfo(*sys.exc_info())
            report.set_interrupted(exc_info)
        return report
