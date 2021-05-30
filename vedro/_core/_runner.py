import sys
from time import time
from typing import List

from .._events import (
    ScenarioFailEvent,
    ScenarioPassEvent,
    ScenarioRunEvent,
    ScenarioSkipEvent,
    StepFailEvent,
    StepPassEvent,
    StepRunEvent,
)
from .._scenario import Scenario
from ._dispatcher import Dispatcher
from ._exc_info import ExcInfo
from ._report import Report
from ._scenario_result import ScenarioResult
from ._step_result import StepResult
from ._virtual_scenario import VirtualScenario
from ._virtual_step import VirtualStep

__all__ = ("Runner",)


class Runner:
    def __init__(self, dispatcher: Dispatcher) -> None:
        self._dispatcher = dispatcher

    async def run_step(self, step: VirtualStep, scope: Scenario) -> StepResult:
        step_result = StepResult(step)

        await self._dispatcher.fire(StepRunEvent(step_result))
        step_result.set_started_at(time())
        try:
            if step.is_coro():
                await step(scope)
            else:
                step(scope)
        except:  # noqa: E722
            step_result.set_ended_at(time())
            exc_info = ExcInfo(*sys.exc_info())
            step_result.set_exc_info(exc_info)
            step_result.mark_failed()
            await self._dispatcher.fire(StepFailEvent(step_result))
        else:
            step_result.set_ended_at(time())
            step_result.mark_passed()
            await self._dispatcher.fire(StepPassEvent(step_result))

        return step_result

    async def run_scenario(self, scenario: VirtualScenario) -> ScenarioResult:
        scenario_result = ScenarioResult(scenario)
        scope = scenario()

        if scenario.is_skipped():
            scenario_result.mark_skipped()
            await self._dispatcher.fire(ScenarioSkipEvent(scenario_result))
            return scenario_result

        await self._dispatcher.fire(ScenarioRunEvent(scenario_result))
        scenario_result.set_started_at(time())
        for step in scenario.steps:
            step_result = await self.run_step(step, scope)
            scenario_result.add_step_result(step_result)

            if step_result.is_failed():
                scenario_result.set_ended_at(time())
                scenario_result.mark_failed()
                await self._dispatcher.fire(ScenarioFailEvent(scenario_result))
                break

        if not scenario_result.is_failed():
            scenario_result.set_ended_at(time())
            scenario_result.mark_passed()
            await self._dispatcher.fire(ScenarioPassEvent(scenario_result))

        return scenario_result

    async def run(self, scenarios: List[VirtualScenario]) -> Report:
        report = Report()
        for scenario in scenarios:
            scenario_result = await self.run_scenario(scenario)
            report.add_result(scenario_result)
        return report
