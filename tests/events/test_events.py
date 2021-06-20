from argparse import ArgumentParser, Namespace
from unittest.mock import Mock

from baby_steps import given, then, when
from pytest import raises

from vedro._core import Report, ScenarioResult, StepResult, VirtualScenario, VirtualStep
from vedro._events import (
    ArgParsedEvent,
    ArgParseEvent,
    CleanupEvent,
    Event,
    ScenarioFailEvent,
    ScenarioPassEvent,
    ScenarioRunEvent,
    ScenarioSkipEvent,
    StartupEvent,
    StepFailEvent,
    StepPassEvent,
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


def test_scenario_skip_event():
    with given:
        scenario_ = Mock(VirtualScenario)
        scenario_result = ScenarioResult(scenario_)

    with when:
        event = ScenarioSkipEvent(scenario_result)

    with then:
        assert event.scenario_result == scenario_result
        assert repr(event) == f"ScenarioSkipEvent({scenario_result!r})"


def test_scenario_run_event():
    with given:
        scenario_ = Mock(VirtualScenario)
        scenario_result = ScenarioResult(scenario_)

    with when:
        event = ScenarioRunEvent(scenario_result)

    with then:
        assert event.scenario_result == scenario_result
        assert repr(event) == f"ScenarioRunEvent({scenario_result!r})"


def test_scenario_fail_event():
    with given:
        scenario_ = Mock(VirtualScenario)
        scenario_result = ScenarioResult(scenario_)

    with when:
        event = ScenarioFailEvent(scenario_result)

    with then:
        assert event.scenario_result == scenario_result
        assert repr(event) == f"ScenarioFailEvent({scenario_result!r})"


def test_scenario_pass_event():
    with given:
        scenario_ = Mock(VirtualScenario)
        scenario_result = ScenarioResult(scenario_)

    with when:
        event = ScenarioPassEvent(scenario_result)

    with then:
        assert event.scenario_result == scenario_result
        assert repr(event) == f"ScenarioPassEvent({scenario_result!r})"


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
        event = StepFailEvent(step_result)

    with then:
        assert event.step_result == step_result
        assert repr(event) == f"StepFailEvent({step_result!r})"


def test_step_pass_event():
    with given:
        step_ = Mock(VirtualStep)
        step_result = StepResult(step_)

    with when:
        event = StepPassEvent(step_result)

    with then:
        assert event.step_result == step_result
        assert repr(event) == f"StepPassEvent({step_result!r})"


def test_cleanup_event():
    with given:
        report = Report()

    with when:
        event = CleanupEvent(report)

    with then:
        assert event.report == report
        assert repr(event) == f"CleanupEvent({report!r})"
