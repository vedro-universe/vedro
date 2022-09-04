from time import time
from typing import List, Tuple, Type

from vedro.core import (
    Dispatcher,
    Report,
    ScenarioResult,
    ScenarioRunner,
    ScenarioScheduler,
    StepResult,
    VirtualScenario,
    VirtualStep,
)
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
    def __init__(self, dispatcher: Dispatcher,
                 interrupt_exceptions: Tuple[Type[BaseException], ...] = ()) -> None:
        self._dispatcher = dispatcher
        self._interrupt_exceptions = interrupt_exceptions

    async def run_step(self, step: VirtualStep) -> StepResult:
        step_result = StepResult(step)

        await self._dispatcher.fire(StepRunEvent(step_result))
        step_result.set_started_at(time()).set_ended_at(time())
        step_result.mark_passed()
        await self._dispatcher.fire(StepPassedEvent(step_result))

        return step_result

    async def run_scenario(self, scenario: VirtualScenario) -> ScenarioResult:
        scenario_result = ScenarioResult(scenario)
        # ref = scenario()
        scenario_result.set_scope({})

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
