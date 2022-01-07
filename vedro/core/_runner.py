import sys
from time import time
from typing import List, Tuple, Type

from .._scenario import Scenario
from ..events import (
    ExceptionRaisedEvent,
    ScenarioFailedEvent,
    ScenarioPassedEvent,
    ScenarioRunEvent,
    ScenarioSkippedEvent,
    StepFailedEvent,
    StepPassedEvent,
    StepRunEvent,
)
from ._dispatcher import Dispatcher
from ._exc_info import ExcInfo
from ._report import Report
from ._scenario_result import ScenarioResult
from ._step_result import StepResult
from ._virtual_scenario import VirtualScenario
from ._virtual_step import VirtualStep

__all__ = ("Runner",)


class _ScenarioInitError(Exception):
    pass


class Runner:
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

    async def run_scenario(self, scenario: VirtualScenario, *, rerun: int = 0) -> ScenarioResult:
        scenario_result = ScenarioResult(scenario, rerun=rerun)
        try:
            ref = scenario()
        except:  # noqa: E722
            message = (f"Can't initialize scenario {scenario_result.scenario.subject!r} "
                       f"at {scenario_result.scenario.path}")
            raise _ScenarioInitError(message)
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

    def _get_aggregated_result(self, scenario_results: List[ScenarioResult]) -> ScenarioResult:
        passed, failed = [], []
        for scenario_result in scenario_results:
            if scenario_result.is_passed():
                passed.append(scenario_result)
            else:
                failed.append(scenario_result)

        resolution = passed[-1] if len(passed) > len(failed) else failed[-1]

        aggregated = ScenarioResult(resolution.scenario)
        for step_result in resolution.step_results:
            aggregated.add_step_result(step_result)
        aggregated.set_scope(resolution.scope)

        if scenario_results[0].started_at:
            aggregated.set_started_at(scenario_results[0].started_at)
        if scenario_results[-1].ended_at:
            aggregated.set_ended_at(scenario_results[-1].ended_at)

        return aggregated.mark_passed() if resolution.is_passed() else aggregated.mark_failed()

    async def run(self, scenarios: List[VirtualScenario], reruns: int = 0) -> Report:
        report = Report()

        for scenario in scenarios:
            scenario_result = await self.run_scenario(scenario)
            if not scenario_result.is_failed() or reruns == 0:
                report.add_result(scenario_result)
                continue

            scenario_results = [scenario_result]
            for rerun in range(1, reruns + 1):
                scenario_result = await self.run_scenario(scenario, rerun=rerun)
                scenario_results.append(scenario_result)

            aggregated_result = self._get_aggregated_result(scenario_results)
            report.add_result(aggregated_result)

        return report
