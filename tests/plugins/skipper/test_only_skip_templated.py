import sys
from os import linesep
from typing import Any, cast

import pytest
from baby_steps import then, when

from vedro import Scenario, params
from vedro.plugins.skipper import only, skip

from ._utils import get_only_attr, get_scenarios, get_skip_attr

# pytest.mark.skipif does not work as expected
# Also global "if sys.version_info >= (3, 9)" does not work as expected with pytest
# (SyntaxError: invalid syntax)
if sys.version_info < (3, 9):
    params_decorator = cast(Any, params)
else:
    params_decorator = cast(Any, params)
    params_decorator_py39 = linesep.join([
        "def params_decorator(decorator = None):",
        "    return params[decorator]() if decorator else params()",
    ])
    code_object = compile(params_decorator_py39, "<string>", "exec")
    exec(code_object)


@pytest.mark.skipif(sys.version_info < (3, 9), reason="requires python3.9 or higher")
def test_template_only_empty():
    with when:
        class OnlyEmptyScenario(Scenario):
            @params_decorator(only)
            @params_decorator()
            def __init__(self):
                pass

    with then:
        scenarios = get_scenarios("OnlyEmptyScenario", globals())
        assert len(scenarios) == 2
        assert get_only_attr(scenarios[0]) is True
        assert get_only_attr(scenarios[1]) is False


@pytest.mark.skipif(sys.version_info < (3, 9), reason="requires python3.9 or higher")
def test_only_template_only_empty():
    with when:
        @only
        class TemplateOnlyEmptyScenario(Scenario):
            @params_decorator(only)
            @params_decorator()
            def __init__(self):
                pass

    with then:
        scenarios = get_scenarios("TemplateOnlyEmptyScenario", globals())
        assert len(scenarios) == 2
        assert get_only_attr(scenarios[0]) is True
        assert get_only_attr(scenarios[1]) is False


@pytest.mark.skipif(sys.version_info < (3, 9), reason="requires python3.9 or higher")
def test_only_template_only_only():
    with when:
        @only
        class TemplateOnlyOnlyScenario(Scenario):
            @params_decorator(only)
            @params_decorator(only)
            def __init__(self):
                pass

    with then:
        scenarios = get_scenarios("TemplateOnlyOnlyScenario", globals())
        assert len(scenarios) == 2
        assert get_only_attr(scenarios[0]) is True
        assert get_only_attr(scenarios[1]) is True


@pytest.mark.skipif(sys.version_info < (3, 9), reason="requires python3.9 or higher")
def test_only_template_only_skip():
    with when:
        @only
        class TemplateOnlySkipScenario(Scenario):
            @params_decorator(only)
            @params_decorator(skip)
            def __init__(self):
                pass

    with then:
        scenarios = get_scenarios("TemplateOnlySkipScenario", globals())
        assert len(scenarios) == 2
        assert get_only_attr(scenarios[0]) is True
        assert get_only_attr(scenarios[1]) is False


@pytest.mark.skipif(sys.version_info < (3, 9), reason="requires python3.9 or higher")
def test_template_skip_empty():
    with when:
        class SkipEmptyScenario(Scenario):
            @params_decorator(skip)
            @params_decorator()
            def __init__(self):
                pass

    with then:
        scenarios = get_scenarios("SkipEmptyScenario", globals())
        assert len(scenarios) == 2
        assert get_skip_attr(scenarios[0]) is True
        assert get_skip_attr(scenarios[1]) is False


@pytest.mark.skipif(sys.version_info < (3, 9), reason="requires python3.9 or higher")
def test_skip_template_skip_empty():
    with when:
        @skip
        class TemplateSkipEmptyScenario(Scenario):
            @params_decorator(skip)
            @params_decorator()
            def __init__(self):
                pass

    with then:
        scenarios = get_scenarios("TemplateSkipEmptyScenario", globals())
        assert len(scenarios) == 2
        assert get_skip_attr(scenarios[0]) is True
        assert get_skip_attr(scenarios[1]) is False


@pytest.mark.skipif(sys.version_info < (3, 9), reason="requires python3.9 or higher")
def test_skip_template_skip_skip():
    with when:
        @skip
        class TemplateSkipSkipScenario(Scenario):
            @params_decorator(skip)
            @params_decorator(skip)
            def __init__(self):
                pass

    with then:
        scenarios = get_scenarios("TemplateSkipSkipScenario", globals())
        assert len(scenarios) == 2
        assert get_skip_attr(scenarios[0]) is True
        assert get_skip_attr(scenarios[1]) is True


@pytest.mark.skipif(sys.version_info < (3, 9), reason="requires python3.9 or higher")
def test_skip_template_skip_only():
    with when:
        @skip
        class TemplateSkipOnlyScenario(Scenario):
            @params_decorator(skip)
            @params_decorator(only)
            def __init__(self):
                pass

    with then:
        scenarios = get_scenarios("TemplateSkipOnlyScenario", globals())
        assert len(scenarios) == 2
        assert get_skip_attr(scenarios[0]) is True
        assert get_skip_attr(scenarios[1]) is False
