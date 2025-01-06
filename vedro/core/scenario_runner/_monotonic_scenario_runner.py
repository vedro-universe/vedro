import os
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
from .._step_result import StepResult
from .._virtual_scenario import VirtualScenario
from .._virtual_step import VirtualStep
from ..scenario_result import ScenarioResult
from ..scenario_scheduler import ScenarioScheduler
from ._interrupted import Interrupted, RunInterrupted, ScenarioInterrupted, StepInterrupted
from ._scenario_runner import ScenarioRunner

__all__ = ("MonotonicScenarioRunner",)


class MonotonicScenarioRunner(ScenarioRunner):
    """
    Represents a scenario runner that executes scenarios in a monotonic order.

    This runner is responsible for managing the execution of scenarios and their steps,
    firing events during the process, and handling interruptions.
    """

    def __init__(self, dispatcher: Dispatcher, *,
                 interrupt_exceptions: Tuple[Type[BaseException], ...] = ()) -> None:
        """
        Initialize the MonotonicScenarioRunner.

        :param dispatcher: The dispatcher used to fire events during the execution process.
        :param interrupt_exceptions: A tuple of exceptions that should interrupt the execution.
        """
        self._dispatcher = dispatcher
        assert isinstance(interrupt_exceptions, tuple)
        self._interrupt_exceptions = interrupt_exceptions + (Interrupted,)

    def _is_interruption(self, exc_info: ExcInfo,
                         exceptions: Tuple[Type[BaseException], ...]) -> bool:
        """
        Check if the given exception matches one of the interruption exceptions.

        :param exc_info: The exception information.
        :param exceptions: A tuple of exception types to check against.
        :return: True if the exception matches one of the interruption exceptions, False otherwise.
        """
        for exception in exceptions:
            if isinstance(exc_info.value, exception):
                return True
        return False

    async def run_step(self, step: VirtualStep, ref: Scenario) -> StepResult:
        """
        Execute a single step of a scenario.

        This method handles both synchronous and asynchronous steps, fires events
        during execution, and manages exceptions raised during the step.

        :param step: The virtual step to be executed.
        :param ref: The reference to the scenario instance.
        :return: The result of the step execution.
        :raises StepInterrupted: If the step execution is interrupted.
        """
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
        """
        Execute a single scenario and its associated steps.

        This method fires events during execution, handles skipped scenarios,
        and manages interruptions or failures within the scenario.

        :param scenario: The virtual scenario to be executed.
        :return: The result of the scenario execution.
        :raises ScenarioInterrupted: If the scenario execution is interrupted.
        """
        scenario_result = ScenarioResult(scenario)

        if scenario.is_skipped():
            scenario_result.mark_skipped()
            await self._dispatcher.fire(ScenarioSkippedEvent(scenario_result))
            return scenario_result

        os.chdir(scenario._project_dir)  # TODO: Avoid using private attributes directly
        await self._dispatcher.fire(ScenarioRunEvent(scenario_result))
        scenario_result.set_started_at(time())

        ref = scenario()
        scenario_result.set_scope(ref.__dict__)

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
        """
        Report the results of a scenario's executions.

        This method aggregates the results of the scenario's executions and adds
        them to the report. It also fires a `ScenarioReportedEvent`.

        :param scenario_results: A list of scenario results to report.
        :param report: The report object to which results are added.
        :param scheduler: The scheduler used to aggregate the scenario results.
        """
        aggregated_result = scheduler.aggregate_results(scenario_results)
        report.add_result(aggregated_result)
        await self._dispatcher.fire(ScenarioReportedEvent(aggregated_result))

    async def _run_scenarios(self, scheduler: ScenarioScheduler, report: Report) -> None:
        """
        Execute all scenarios provided by the scheduler.

        This method manages scenario execution, aggregates results, and handles interruptions.

        :param scheduler: The scheduler providing scenarios to execute.
        :param report: The report object to which results are added.
        :raises RunInterrupted: If the execution is interrupted by an exception.
        """
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
        """
        Execute all scenarios and return the final report.

        This method manages the execution of all scenarios provided by the scheduler
        and handles any interruptions during the process.

        :param scheduler: The scheduler providing scenarios to execute.
        :return: The final report containing all results and any interruption information.
        """
        report = Report()
        try:
            await self._run_scenarios(scheduler, report)
        except self._interrupt_exceptions as e:
            exc_info = e.exc_info if isinstance(e, RunInterrupted) else ExcInfo(*sys.exc_info())
            report.set_interrupted(exc_info)
        return report
