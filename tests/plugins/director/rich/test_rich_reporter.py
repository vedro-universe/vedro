import os
from argparse import ArgumentParser, Namespace
from pathlib import Path
from typing import List, Optional
from unittest.mock import Mock, call

import pytest
from baby_steps import given, then, when
from rich.console import Console
from rich.style import Style

from vedro._core import (
    Dispatcher,
    ExcInfo,
    Report,
    ScenarioResult,
    StepResult,
    VirtualScenario,
    VirtualStep,
)
from vedro._events import (
    ArgParsedEvent,
    ArgParseEvent,
    CleanupEvent,
    ScenarioFailEvent,
    ScenarioPassEvent,
    ScenarioRunEvent,
    ScenarioSkipEvent,
    StartupEvent,
)
from vedro.plugins.director import RichReporter


@pytest.fixture()
def dispatcher():
    return Dispatcher()


@pytest.fixture()
def console_():
    return Mock(Console)


@pytest.fixture()
def reporter(console_):
    return RichReporter(lambda: console_)


def make_scenario_path(path: str = "", name: str = "scenario.py") -> Path:
    return Path(os.getcwd()) / "scenarios" / path / name


def make_scenario_result(*, scenario_path: Optional[Path] = None,
                         scenario_subject: Optional[str] = None,
                         step_results: Optional[List[StepResult]] = None) -> ScenarioResult:
    scenario_ = Mock(VirtualScenario)
    scenario_.path = scenario_path if scenario_path else make_scenario_path()
    scenario_.subject = scenario_subject

    scenario_result = ScenarioResult(scenario_)
    if step_results:
        for step_result in step_results:
            scenario_result.add_step_result(step_result)
    return scenario_result


def make_step_result(name: Optional[str] = None) -> StepResult:
    step_ = Mock(VirtualStep)
    step_.name = name if step_ else str(step_)
    return StepResult(step_)


def make_exc_info(value: Exception) -> ExcInfo:
    return ExcInfo(type(value), value, None)


@pytest.mark.asyncio
async def test_rich_reporter_arg_parse_event(*, dispatcher: Dispatcher,
                                             reporter: RichReporter, console_: Mock):
    with given:
        reporter.subscribe(dispatcher)

        parser = ArgumentParser()
        event = ArgParseEvent(parser)

    with when:
        await dispatcher.fire(event)

    with then:
        assert console_.mock_calls == []


@pytest.mark.asyncio
async def test_rich_reporter_arg_parsed_event(*, dispatcher: Dispatcher,
                                              reporter: RichReporter, console_: Mock):
    with given:
        reporter.subscribe(dispatcher)

        args = Namespace(verbose=0)
        event = ArgParsedEvent(args)

    with when:
        await dispatcher.fire(event)

    with then:
        assert console_.mock_calls == []


@pytest.mark.asyncio
async def test_rich_reporter_startup_event(*, dispatcher: Dispatcher,
                                           reporter: RichReporter, console_: Mock):
    with given:
        reporter.subscribe(dispatcher)
        event = StartupEvent([])

    with when:
        await dispatcher.fire(event)

    with then:
        assert console_.mock_calls == [
            call.print("Scenarios")
        ]


@pytest.mark.asyncio
async def test_rich_reporter_scenario_run_event(*, dispatcher: Dispatcher,
                                                reporter: RichReporter, console_: Mock):
    with given:
        reporter.subscribe(dispatcher)

        namespace = "<namespace>"
        scenario_result = make_scenario_result(scenario_path=make_scenario_path(namespace))
        event = ScenarioRunEvent(scenario_result)

    with when:
        await dispatcher.fire(event)

    with then:
        assert console_.mock_calls == [
            call.print(f"* {namespace}", style=Style.parse("bold"))
        ]


@pytest.mark.asyncio
async def test_rich_reporter_scenario_run_event_same_namespace(*, dispatcher: Dispatcher,
                                                               reporter: RichReporter,
                                                               console_: Mock):
    with given:
        reporter.subscribe(dispatcher)

        namespace = "<namespace>"
        scenario_result = make_scenario_result(scenario_path=make_scenario_path(namespace))
        event = ScenarioRunEvent(scenario_result)
        await dispatcher.fire(event)
        console_.reset_mock()

    with when:
        await dispatcher.fire(event)

    with then:
        assert console_.mock_calls == []


@pytest.mark.asyncio
async def test_rich_reporter_scenario_run_event_diff_namespace(*, dispatcher: Dispatcher,
                                                               reporter: RichReporter,
                                                               console_: Mock):
    with given:
        reporter.subscribe(dispatcher)

        namespace1 = "<namespace1>"
        scenario_result1 = make_scenario_result(scenario_path=make_scenario_path(namespace1))
        event1 = ScenarioRunEvent(scenario_result1)
        await dispatcher.fire(event1)
        console_.reset_mock()

        namespace2 = "<namespace2>"
        scenario_result2 = make_scenario_result(scenario_path=make_scenario_path(namespace2))
        event2 = ScenarioRunEvent(scenario_result2)

    with when:
        await dispatcher.fire(event2)

    with then:
        assert console_.mock_calls == [
            call.print(f"* {namespace2}", style=Style.parse("bold")),
        ]


@pytest.mark.asyncio
async def test_rich_reporter_scenario_skip_event(*, dispatcher: Dispatcher,
                                                 reporter: RichReporter, console_: Mock):
    with given:
        reporter.subscribe(dispatcher)

        scenario_result = make_scenario_result()
        event = ScenarioSkipEvent(scenario_result)

    with when:
        await dispatcher.fire(event)

    with then:
        assert console_.mock_calls == []


@pytest.mark.asyncio
async def test_rich_reporter_scenario_pass_event(*, dispatcher: Dispatcher,
                                                 reporter: RichReporter, console_: Mock):
    with given:
        reporter.subscribe(dispatcher)

        subject = "<subject>"
        scenario_result = make_scenario_result(scenario_subject=subject)
        event = ScenarioPassEvent(scenario_result)

    with when:
        await dispatcher.fire(event)

    with then:
        assert console_.mock_calls == [
            call.print(f" ✔ {subject}", style=Style.parse("green"))
        ]


@pytest.mark.asyncio
async def test_rich_reporter_scenario_fail_event_default_verbose(*, dispatcher: Dispatcher,
                                                                 reporter: RichReporter,
                                                                 console_: Mock):
    with given:
        reporter.subscribe(dispatcher)

        subject = "<subject>"
        scenario_result = make_scenario_result(scenario_subject=subject)
        event = ScenarioFailEvent(scenario_result)

    with when:
        await dispatcher.fire(event)

    with then:
        assert console_.mock_calls == [
            call.print(f" ✗ {subject}", style=Style.parse("red"))
        ]


@pytest.mark.asyncio
async def test_rich_reporter_scenario_fail_event_verbose0(*, dispatcher: Dispatcher,
                                                          reporter: RichReporter,
                                                          console_: Mock):
    with given:
        reporter.subscribe(dispatcher)
        event = ArgParsedEvent(Namespace(verbose=0))
        await dispatcher.fire(event)

        scenario_result = make_scenario_result()
        event = ScenarioFailEvent(scenario_result)

    with when:
        await dispatcher.fire(event)

    with then:
        assert console_.mock_calls == [
            call.print(f" ✗ {scenario_result.scenario_subject}", style=Style.parse("red"))
        ]


@pytest.mark.asyncio
async def test_rich_reporter_scenario_fail_event_verbose1(*, dispatcher: Dispatcher,
                                                          reporter: RichReporter,
                                                          console_: Mock):
    with given:
        reporter.subscribe(dispatcher)
        event = ArgParsedEvent(Namespace(verbose=1))
        await dispatcher.fire(event)

        step_name_passed = "<passed step>"
        step_result_passed = make_step_result(step_name_passed).mark_passed()
        step_name_failed = "<failed step>"
        step_result_failed = make_step_result(step_name_failed).mark_failed()
        step_result = make_step_result()

        scenario_result = make_scenario_result(step_results=[
            step_result_passed,
            step_result_failed,
            step_result,
        ])
        event = ScenarioFailEvent(scenario_result)

    with when:
        await dispatcher.fire(event)

    with then:
        assert console_.mock_calls == [
            call.print(f" ✗ {scenario_result.scenario_subject}", style=Style.parse("red")),
            call.print(f"    ✔ {step_name_passed}", style=Style.parse("green")),
            call.print(f"    ✗ {step_name_failed}", style=Style.parse("red")),
        ]


@pytest.mark.asyncio
async def test_rich_reporter_scenario_fail_event_verbose2(*, dispatcher: Dispatcher,
                                                          reporter: RichReporter,
                                                          console_: Mock):
    with given:
        reporter.subscribe(dispatcher)
        event = ArgParsedEvent(Namespace(verbose=2))
        await dispatcher.fire(event)

        step_result_passed = make_step_result().mark_passed()
        step_result_failed = make_step_result().mark_failed()

        exc_info = make_exc_info(AssertionError())
        step_result_failed.set_exc_info(exc_info)
        step_result = make_step_result()

        scenario_result = make_scenario_result(step_results=[
            step_result_passed,
            step_result_failed,
            step_result,
        ])
        event = ScenarioFailEvent(scenario_result)

    with when:
        await dispatcher.fire(event)

    with then:
        assert console_.mock_calls == [
            call.print(f" ✗ {scenario_result.scenario_subject}", style=Style.parse("red")),
            call.print(f"    ✔ {step_result_passed.step_name}", style=Style.parse("green")),
            call.print(f"    ✗ {step_result_failed.step_name}", style=Style.parse("red")),
            call.print("AssertionError\n", style=Style.parse("yellow")),
        ]


@pytest.mark.asyncio
async def test_rich_reporter_scenario_fail_event_verbose3(*, dispatcher: Dispatcher,
                                                          reporter: RichReporter,
                                                          console_: Mock):
    with given:
        reporter.subscribe(dispatcher)
        event = ArgParsedEvent(Namespace(verbose=3))
        await dispatcher.fire(event)

        step_result_passed = make_step_result("<passed step>").mark_passed()
        step_result_failed = make_step_result("<failed step>").mark_failed()
        exc_info = make_exc_info(AssertionError())
        step_result_failed.set_exc_info(exc_info)
        step_result = make_step_result()

        scenario_result = make_scenario_result(step_results=[
            step_result_passed,
            step_result_failed,
            step_result,
        ])
        scenario_result.set_scope({"key_int": 1, "key_str": "val"})
        event = ScenarioFailEvent(scenario_result)

    with when:
        await dispatcher.fire(event)

    with then:
        assert console_.mock_calls == [
            call.print(f" ✗ {scenario_result.scenario_subject}", style=Style.parse("red")),
            call.print(f"    ✔ {step_result_passed.step_name}", style=Style.parse("green")),
            call.print(f"    ✗ {step_result_failed.step_name}", style=Style.parse("red")),
            call.print("AssertionError\n", style=Style.parse("yellow")),
            call.print("Scope:", style=Style.parse("bold blue")),
            call.print(" key_int: ", end="", style=Style.parse("blue")),
            call.print("1"),
            call.print(" key_str: ", end="", style=Style.parse("blue")),
            call.print('"val"'),
            call.print(),
        ]


@pytest.mark.asyncio
async def test_rich_reporter_scenario_fail_event_without_steps_verbose3(*, dispatcher: Dispatcher,
                                                                        reporter: RichReporter,
                                                                        console_: Mock):
    with given:
        reporter.subscribe(dispatcher)
        event = ArgParsedEvent(Namespace(verbose=3))
        await dispatcher.fire(event)

        scenario_result = make_scenario_result()
        scenario_result.set_scope({})
        event = ScenarioFailEvent(scenario_result)

    with when:
        await dispatcher.fire(event)

    with then:
        assert console_.mock_calls == [
            call.print(f" ✗ {scenario_result.scenario_subject}", style=Style.parse("red")),
        ]


@pytest.mark.asyncio
async def test_rich_reporter_cleanup_event(*, dispatcher: Dispatcher):
    with given:
        console_ = Mock()
        reporter = RichReporter(lambda: console_)
        reporter.subscribe(dispatcher)

        report = Report()
        event = CleanupEvent(report)

    with when:
        await dispatcher.fire(event)

    with then:
        assert console_.mock_calls == [
            call.print(),
            call.print("# 0 scenarios, 0 passed, 0 failed, 0 skipped",
                       style=Style.parse("bold red"), end=""),
            call.print(" (0.00s)", style=Style.parse("blue"))
        ]


@pytest.mark.asyncio
async def test_rich_reporter_success_cleanup_event(*, dispatcher: Dispatcher,
                                                   reporter: RichReporter, console_: Mock):
    with given:
        reporter.subscribe(dispatcher)

        report = Report()
        scenario_result1 = make_scenario_result().mark_passed()
        scenario_result1.set_started_at(1.0)
        scenario_result1.set_ended_at(2.0)
        report.add_result(scenario_result1)

        scenario_result2 = make_scenario_result().mark_passed()
        scenario_result2.set_started_at(2.0)
        scenario_result2.set_ended_at(3.0)
        report.add_result(scenario_result2)

        scenario_result3 = make_scenario_result().mark_skipped()
        report.add_result(scenario_result3)
        event = CleanupEvent(report)

    with when:
        await dispatcher.fire(event)

    with then:
        assert console_.mock_calls == [
            call.print(),
            call.print("# 3 scenarios, 2 passed, 0 failed, 1 skipped",
                       style=Style.parse("bold green"),
                       end=""),
            call.print(" (2.00s)", style=Style.parse("blue"))
        ]


@pytest.mark.asyncio
async def test_rich_reporter_failed_cleanup_event(*, dispatcher: Dispatcher,
                                                  reporter: RichReporter, console_: Mock):
    with given:
        reporter.subscribe(dispatcher)

        report = Report()
        scenario_result = make_scenario_result().mark_failed()
        scenario_result.set_started_at(3.145)
        scenario_result.set_ended_at(6.285)
        report.add_result(scenario_result)

        event = CleanupEvent(report)

    with when:
        await dispatcher.fire(event)

    with then:
        assert console_.mock_calls == [
            call.print(),
            call.print("# 1 scenarios, 0 passed, 1 failed, 0 skipped",
                       style=Style.parse("bold red"),
                       end=""),
            call.print(" (3.14s)", style=Style.parse("blue"))
        ]
