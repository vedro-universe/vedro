import os
from pathlib import Path
from types import MethodType
from typing import Type
from unittest.mock import Mock

import pytest
from baby_steps import given, then, when
from pytest import raises

from vedro import Scenario
from vedro.core import Plugin, PluginConfig, VirtualScenario, VirtualStep
from vedro.core._virtual_scenario import ScenarioInitError


@pytest.fixture()
def scenario_():
    scenario = Mock(Scenario)
    scenario.__file__ = os.getcwd() + "/scenarios/scenario.py"
    scenario.__module__ = "scenarios.scenario"
    scenario.__name__ = "Scenario"
    return scenario


@pytest.fixture()
def template_():
    scenario = Mock(Scenario)
    scenario.__file__ = os.getcwd() + "/scenarios/scenario.py"
    scenario.__module__ = "scenarios.scenario"
    scenario.__name__ = "Scenario_0_VedroScenario"
    scenario.__vedro__template_index__ = 0
    scenario.__vedro__template_total__ = 1
    return scenario


@pytest.fixture()
def method_():
    return Mock(MethodType)


def test_virtual_scenario_steps(*, scenario_: Type[Scenario], method_: MethodType):
    with given:
        expected_steps = [VirtualStep(method_), VirtualStep(method_)]
        virtual_scenario = VirtualScenario(scenario_, expected_steps)

    with when:
        actual_steps = virtual_scenario.steps

    with then:
        assert actual_steps == expected_steps


def test_virtual_scenario_unique_id(*, scenario_: Type[Scenario]):
    with given:
        virtual_scenario = VirtualScenario(scenario_, [])

    with when:
        unique_id = virtual_scenario.unique_id

    with then:
        assert unique_id == "scenarios/scenario.py::Scenario"


def test_virtual_scenario_unique_hash(*, scenario_: Type[Scenario]):
    with given:
        virtual_scenario = VirtualScenario(scenario_, [])

    with when:
        unique_hash = virtual_scenario.unique_hash

    with then:
        assert unique_hash == "c6b074186cf075e2044bed1088c30b9af5e6e2c2"


def test_virtual_template_unique_id(*, template_: Type[Scenario]):
    with given:
        virtual_scenario = VirtualScenario(template_, [])

    with when:
        unique_id = virtual_scenario.unique_id

    with then:
        assert unique_id == "scenarios/scenario.py::Scenario_0_VedroScenario#0"


def test_virtual_scenario_path(*, scenario_: Type[Scenario]):
    with given:
        virtual_scenario = VirtualScenario(scenario_, [])

    with when:
        path = virtual_scenario.path

    with then:
        assert path == Path(scenario_.__file__)


def test_virtual_scenario_rel_path(*, scenario_: Type[Scenario]):
    with given:
        virtual_scenario = VirtualScenario(scenario_, [])

    with when:
        path = virtual_scenario.rel_path

    with then:
        assert path == Path("scenarios/scenario.py")


def test_virtual_scenario_subject(*, scenario_: Type[Scenario]):
    with given:
        scenario_.subject = "<subject>"
        virtual_scenario = VirtualScenario(scenario_, [])

    with when:
        subject = virtual_scenario.subject

    with then:
        assert subject == scenario_.subject


def test_virtual_scenario_without_subject(*, scenario_: Type[Scenario]):
    with given:
        virtual_scenario = VirtualScenario(scenario_, [])

    with when:
        subject = virtual_scenario.subject

    with then:
        assert subject == Path(scenario_.__file__).stem


def test_virtual_scenario_namespace(*, scenario_: Type[Scenario]):
    with given:
        virtual_scenario = VirtualScenario(scenario_, [])

    with when:
        namespace = virtual_scenario.namespace

    with then:
        assert namespace == ""


def test_virtual_scenario_with_subject(*, scenario_: Type[Scenario]):
    with given:
        scenario_.subject = "<subject>"
        virtual_scenario = VirtualScenario(scenario_, [])

    with when:
        subject = virtual_scenario.subject

    with then:
        assert subject == scenario_.subject


def test_virtual_scenario_is_skipped(*, scenario_: Type[Scenario]):
    with given:
        virtual_scenario = VirtualScenario(scenario_, [])

    with when:
        is_skipped = virtual_scenario.is_skipped()

    with then:
        assert is_skipped is False


def test_virtual_scenario_skip(*, scenario_: Type[Scenario]):
    with given:
        virtual_scenario = VirtualScenario(scenario_, [])

    with when:
        res = virtual_scenario.skip()

    with then:
        assert res is None
        assert virtual_scenario.is_skipped() is True
        assert virtual_scenario.skip_reason is None


def test_virtual_scenario_skip_with_reason(*, scenario_: Type[Scenario]):
    with given:
        virtual_scenario = VirtualScenario(scenario_, [])
        reason = "<reason>"

    with when:
        res = virtual_scenario.skip(reason)

    with then:
        assert res is None
        assert virtual_scenario.is_skipped() is True
        assert virtual_scenario.skip_reason == reason


def test_virtual_scenario_init(*, scenario_: Type[Scenario]):
    with given:
        exception = TypeError("<message>")
        scenario_.side_effect = (exception,)
        virtual_scenario = VirtualScenario(scenario_, [])

    with when, raises(BaseException) as exc:
        virtual_scenario()

    with then:
        assert exc.type is ScenarioInitError
        assert str(exc.value) == ('Can\'t initialize scenario "scenario" '
                                  f'at "scenarios/scenario.py" ({exception!r})')


def test_virtual_scenario_repr(*, scenario_: Type[Scenario], method_: MethodType):
    with given:
        steps = [VirtualStep(method_), VirtualStep(method_)]
        virtual_scenario = VirtualScenario(scenario_, steps)

    with when:
        res = repr(virtual_scenario)

    with then:
        assert res == f"<VirtualScenario {str(virtual_scenario.rel_path)!r}>"


def test_virtual_scenario_eq_without_steps(*, scenario_: Type[Scenario]):
    with given:
        virtual_scenario1 = VirtualScenario(scenario_, [])
        virtual_scenario2 = VirtualScenario(scenario_, [])

    with when:
        res = virtual_scenario1 == virtual_scenario2

    with then:
        assert res is True


def test_virtual_scenario_not_eq_without_steps(*, scenario_: Type[Scenario]):
    with given:
        another_scenario_ = Mock(Scenario)
        another_scenario_.__file__ = scenario_.__file__
        another_scenario_.__name__ = scenario_.__name__
        virtual_scenario1 = VirtualScenario(scenario_, [])
        virtual_scenario2 = VirtualScenario(another_scenario_, [])

    with when:
        res = virtual_scenario1 == virtual_scenario2

    with then:
        assert res is False


def test_virtual_scenario_eq_with_steps(*, scenario_: Type[Scenario], method_: MethodType):
    with given:
        steps = [VirtualStep(method_), VirtualStep(method_)]
        virtual_scenario1 = VirtualScenario(scenario_, steps)
        virtual_scenario2 = VirtualScenario(scenario_, steps)

    with when:
        res = virtual_scenario1 == virtual_scenario2

    with then:
        assert res is True


def test_virtual_scenario_not_eq_with_steps(*, scenario_: Type[Scenario], method_: MethodType):
    with given:
        steps = [VirtualStep(method_), VirtualStep(method_)]
        virtual_scenario1 = VirtualScenario(scenario_, steps)

        another_method_ = Mock(MethodType)
        another_steps = [VirtualStep(another_method_), VirtualStep(another_method_)]
        virtual_scenario2 = VirtualScenario(scenario_, another_steps)

    with when:
        res = virtual_scenario1 == virtual_scenario2

    with then:
        assert res is False


def test_set_meta():
    with given:
        class CustomPlugin(Plugin):
            pass

        plugin = CustomPlugin(PluginConfig)

        class CustomScenario(Scenario):
            pass

        virtual_scenario = VirtualScenario(CustomScenario, [])

    with when:
        res = virtual_scenario.set_meta("key", "value", plugin=plugin)

    with then:
        assert res is None


def test_get_meta():
    with given:
        class CustomPlugin(Plugin):
            pass

        plugin = CustomPlugin(PluginConfig)

        class CustomScenario(Scenario):
            pass

        virtual_scenario = VirtualScenario(CustomScenario, [])
        virtual_scenario.set_meta("key", "value", plugin=plugin)

    with when:
        value = virtual_scenario.get_meta("key", plugin=plugin)

    with then:
        assert value == "value"


def test_virtual_scenario_doc():
    with given:
        class CustomScenario(Scenario):
            """My scenario docstring"""
            pass

        virtual_scenario = VirtualScenario(CustomScenario, [])

    with when:
        doc = virtual_scenario.doc

    with then:
        assert doc == "My scenario docstring"


def test_virtual_scenario_doc_multiline():
    with given:
        class CustomScenario(Scenario):
            """
            First line
            Second line
            """
        vs = VirtualScenario(CustomScenario, [])

    with when:
        doc = vs.doc

    with then:
        # `inspect.getdoc` strips indentation & leading blank
        assert doc == "First line\nSecond line"


def test_virtual_scenario_doc_when_absent():
    with given:
        class CustomScenario(Scenario):
            pass  # no docstring here

        virtual_scenario = VirtualScenario(CustomScenario, [])

    with when:
        doc = virtual_scenario.doc

    with then:
        assert doc is None


def test_virtual_scenario_lineno(*, scenario_: Type[Scenario]):
    with given:
        scenario_.__vedro__lineno__ = 42
        virtual_scenario = VirtualScenario(scenario_, [])

    with when:
        lineno = virtual_scenario.lineno

    with then:
        assert lineno == 42


def test_virtual_scenario_no_lineno(*, scenario_: Type[Scenario]):
    with given:
        # __vedro__lineno__ attribute is not set
        virtual_scenario = VirtualScenario(scenario_, [])

    with when:
        lineno = virtual_scenario.lineno

    with then:
        assert lineno is None


def test_virtual_template_lineno(*, template_: Type[Scenario]):
    with given:
        template_.__vedro__lineno__ = 42
        virtual_scenario = VirtualScenario(template_, [])

    with when:
        lineno = virtual_scenario.lineno

    with then:
        assert lineno == 42


def test_virtual_scenario_tags_default_empty():
    with given:
        class CustomScenario(Scenario):
            # No tags attribute defined
            pass

        virtual_scenario = VirtualScenario(CustomScenario, [])

    with when:
        tags = virtual_scenario.tags

    with then:
        assert tags == ()


def test_virtual_scenario_with_tags():
    with given:
        class CustomScenario(Scenario):
            tags = {"API", "P0", "smoke"}

        virtual_scenario = VirtualScenario(CustomScenario, [])

    with when:
        tags = virtual_scenario.tags

    with then:
        assert tags == {"API", "P0", "smoke"}
