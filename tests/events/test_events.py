from argparse import ArgumentParser, Namespace
from unittest.mock import Mock

from baby_steps import given, then, when
from pytest import raises

from vedro._core import ExcInfo, Report, ScenarioResult, StepResult, VirtualScenario, VirtualStep
from vedro.events import (
    ArgParsedEvent,
    ArgParseEvent,
    CleanupEvent,
    Event,
    ExceptionRaisedEvent,
    ScenarioFailedEvent,
    ScenarioPassedEvent,
    ScenarioRunEvent,
    ScenarioSkippedEvent,
    StartupEvent,
    StepFailedEvent,
    StepPassedEvent,
    StepRunEvent,
)


def test_new_event():
    with when:
        class NewEvent(Event):
            pass

    with then:
        assert issubclass(NewEvent, Event)


def test_already_registered_event():
    with given:
        class RegisteredEvent(Event):
            pass

    with when, raises(BaseException) as exception:
        class RegisteredEvent(Event):  # noqa: F811
            pass

    with then:
        assert exception.type is Exception
        assert str(exception.value) == f"Event {RegisteredEvent!r} already registered"


def test_arg_parse_event():
    with given:
        arg_parser = ArgumentParser()

    with when:
        event = ArgParseEvent(arg_parser)

    with then:
        assert event.arg_parser == arg_parser
        assert repr(event) == f"ArgParseEvent({arg_parser!r})"


def test_arg_parsed_event():
    with given:
        namespace = Namespace()

    with when:
        event = ArgParsedEvent(namespace)

    with then:
        assert event.args == namespace
        assert repr(event) == f"ArgParsedEvent({namespace!r})"


def test_startup_event():
    with given:
        scenarios = []

    with when:
        event = StartupEvent(scenarios)

    with then:
        assert event.scenarios == scenarios
        assert repr(event) == f"StartupEvent({scenarios!r})"


def test_scenario_run_event():
    with given:
        scenario_ = Mock(VirtualScenario)
        scenario_result = ScenarioResult(scenario_)

    with when:
        event = ScenarioRunEvent(scenario_result)

    with then:
        assert event.scenario_result == scenario_result
        assert repr(event) == f"ScenarioRunEvent({scenario_result!r})"


def test_scenario_skiped_event():
    with given:
        scenario_ = Mock(VirtualScenario)
        scenario_result = ScenarioResult(scenario_)

    with when:
        event = ScenarioSkippedEvent(scenario_result)

    with then:
        assert event.scenario_result == scenario_result
        assert repr(event) == f"ScenarioSkippedEvent({scenario_result!r})"


def test_scenario_failed_event():
    with given:
        scenario_ = Mock(VirtualScenario)
        scenario_result = ScenarioResult(scenario_)

    with when:
        event = ScenarioFailedEvent(scenario_result)

    with then:
        assert event.scenario_result == scenario_result
        assert repr(event) == f"ScenarioFailedEvent({scenario_result!r})"


def test_scenario_passed_event():
    with given:
        scenario_ = Mock(VirtualScenario)
        scenario_result = ScenarioResult(scenario_)

    with when:
        event = ScenarioPassedEvent(scenario_result)

    with then:
        assert event.scenario_result == scenario_result
        assert repr(event) == f"ScenarioPassedEvent({scenario_result!r})"


def test_step_run_event():
    with given:
        step_ = Mock(VirtualStep)
        step_result = StepResult(step_)

    with when:
        event = StepRunEvent(step_result)

    with then:
        assert event.step_result == step_result
        assert repr(event) == f"StepRunEvent({step_result!r})"


def test_step_fail_event():
    with given:
        step_ = Mock(VirtualStep)
        step_result = StepResult(step_)

    with when:
        event = StepFailedEvent(step_result)

    with then:
        assert event.step_result == step_result
        assert repr(event) == f"StepFailedEvent({step_result!r})"


def test_step_pass_event():
    with given:
        step_ = Mock(VirtualStep)
        step_result = StepResult(step_)

    with when:
        event = StepPassedEvent(step_result)

    with then:
        assert event.step_result == step_result
        assert repr(event) == f"StepPassedEvent({step_result!r})"


def test_exception_raised_event():
    with given:
        exception = AssertionError()
        exc_info = ExcInfo(type(exception), exception, None)

    with when:
        event = ExceptionRaisedEvent(exc_info)

    with then:
        assert event.exc_info == exc_info
        assert repr(event) == f"ExceptionRaisedEvent({exc_info!r})"


def test_cleanup_event():
    with given:
        report = Report()

    with when:
        event = CleanupEvent(report)

    with then:
        assert event.report == report
        assert repr(event) == f"CleanupEvent({report!r})"
