import os
import sys
from time import time
from typing import Any, List, Tuple, Type, cast

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
from ..output_capturer import OutputCapturer
from ..scenario_result import ScenarioResult
from ..scenario_scheduler import ScenarioScheduler
from ._interrupted import Interrupted, RunInterrupted, ScenarioInterrupted, StepInterrupted
from ._scenario_runner import ScenarioRunner

__all__ = ("MonotonicScenarioRunner",)


class MonotonicScenarioRunner(ScenarioRunner):
    """
    A scenario runner that executes scenarios sequentially in a monotonic order.

    This runner manages the execution of scenarios and their steps,
    fires events during the process, and handles interruptions.
    """

    def __init__(self, dispatcher: Dispatcher, *,
                 interrupt_exceptions: Tuple[Type[BaseException], ...] = ()) -> None:
        """
        Initialize the MonotonicScenarioRunner.

        :param dispatcher: The event dispatcher for firing execution events.
        :param interrupt_exceptions: Additional exception types that should interrupt execution.
        """
        self._dispatcher = dispatcher
        assert isinstance(interrupt_exceptions, tuple)
        self._interrupt_exceptions = interrupt_exceptions + (Interrupted,)

    def _is_interruption(self, exc_info: ExcInfo,
                         exceptions: Tuple[Type[BaseException], ...]) -> bool:
        """
        Check if an exception is an interruption exception.

        :param exc_info: The exception information to check.
        :param exceptions: Tuple of exception types to check against.
        :return: True if the exception is an interruption type, False otherwise.
        """
        for exception in exceptions:
            if isinstance(exc_info.value, exception):
                return True
        return False

    async def run_step(self, step: VirtualStep, ref: Scenario, **kwargs: Any) -> StepResult:
        """
        Execute a single step within a scenario.

        Handles both synchronous and asynchronous steps, captures output,
        fires appropriate events, and manages exceptions.

        :param step: The virtual step to execute.
        :param ref: The scenario instance containing the step context.
        :param kwargs: Additional keyword arguments (e.g., output_capturer).
        :return: The result of the step execution.
        :raises StepInterrupted: If the step is interrupted by a configured exception.
        """
        output_capturer = self._get_output_capturer(**kwargs)

        step_result = StepResult(step)

        await self._dispatcher.fire(StepRunEvent(step_result))
        step_result.set_started_at(time())
        try:
            with output_capturer.capture() as captured_output:
                try:
                    if step.is_coro():
                        await step(ref)
                    else:
                        step(ref)
                finally:
                    step_result.set_captured_output(captured_output)
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

    async def run_scenario(self, scenario: VirtualScenario, **kwargs: Any) -> ScenarioResult:
        """
        Execute a complete scenario including all its steps.

        Handles scenario initialization, step execution, output capture,
        and appropriate event firing for skipped, passed, or failed scenarios.

        :param scenario: The virtual scenario to execute.
        :param kwargs: Additional keyword arguments (e.g., output_capturer).
        :return: The result of the scenario execution.
        :raises ScenarioInterrupted: If the scenario is interrupted during execution.
        """
        output_capturer = self._get_output_capturer(**kwargs)

        scenario_result = ScenarioResult(scenario)

        if scenario.is_skipped():
            scenario_result.mark_skipped()
            await self._dispatcher.fire(ScenarioSkippedEvent(scenario_result))
            return scenario_result

        os.chdir(scenario._project_dir)  # TODO: Avoid using private attributes directly
        await self._dispatcher.fire(ScenarioRunEvent(scenario_result))
        scenario_result.set_started_at(time())

        with output_capturer.capture() as captured_output:
            ref = scenario()
        scenario_result.set_captured_output(captured_output)
        scenario_result.set_scope(ref.__dict__)

        for step in scenario.steps:
            try:
                step_result = await self.run_step(step, ref, output_capturer=output_capturer)
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
        Aggregate and report results for a single scenario's multiple executions.

        :param scenario_results: List of results from multiple executions of the same scenario.
        :param report: The report to add aggregated results to.
        :param scheduler: The scheduler used for result aggregation.
        """
        aggregated_result = scheduler.aggregate_results(scenario_results)
        report.add_result(aggregated_result)
        await self._dispatcher.fire(ScenarioReportedEvent(aggregated_result))

    async def _run_scenarios(self,
                             scheduler: ScenarioScheduler,
                             report: Report,
                             **kwargs: Any) -> None:
        """
        Execute all scenarios provided by the scheduler.

        Groups results by scenario unique_id and reports them when switching
        to a different scenario or when execution completes.

        :param scheduler: The scheduler providing scenarios to execute.
        :param report: The report to add results to.
        :param kwargs: Additional keyword arguments (e.g., output_capturer).
        :raises RunInterrupted: If execution is interrupted by a configured exception.
        """
        output_capturer = self._get_output_capturer(**kwargs)

        scenario_results: List[ScenarioResult] = []

        async for scenario in scheduler:
            prev_scenario = scenario_results[-1].scenario if len(scenario_results) > 0 else None
            if prev_scenario and prev_scenario.unique_id != scenario.unique_id:
                await self._report_scenario_results(scenario_results, report, scheduler)
                scenario_results = []

            try:
                scenario_result = await self.run_scenario(scenario,
                                                          output_capturer=output_capturer)
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

    async def run(self, scheduler: ScenarioScheduler, **kwargs: Any) -> Report:
        """
        Execute all scenarios and generate a final report.

        This is the main entry point for running scenarios. It manages the complete
        execution lifecycle and handles any interruptions.

        :param scheduler: The scheduler providing scenarios to execute.
        :param kwargs: Additional keyword arguments (e.g., output_capturer).
        :return: A report containing all execution results and any interruption information.
        """
        output_capturer = self._get_output_capturer(**kwargs)

        report = Report()
        try:
            await self._run_scenarios(scheduler, report, output_capturer=output_capturer)
        except self._interrupt_exceptions as e:
            exc_info = e.exc_info if isinstance(e, RunInterrupted) else ExcInfo(*sys.exc_info())
            report.set_interrupted(exc_info)
        return report

    def _get_output_capturer(self, **kwargs: Any) -> OutputCapturer:
        """
        Retrieve or create an OutputCapturer from kwargs.

        :param kwargs: Keyword arguments potentially containing an output_capturer.
        :return: The OutputCapturer instance.
        """
        return cast(OutputCapturer, kwargs.get("output_capturer", OutputCapturer()))
