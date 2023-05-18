import sys
from functools import partial
from os import linesep
from typing import Any, Dict, List, Type, cast

import pytest
from baby_steps import then, when

from vedro import Scenario, params


def get_scenarios(key: str, globals_: Dict[str, Any]) -> List[Type[Scenario]]:
    return [scn for name, scn in globals_.items() if name.startswith(key)]


def labeled(key, value):
    def wrapped(fn):
        setattr(fn, key, value)
        return fn
    return wrapped


label = partial(labeled, "__label__")
tag = partial(labeled, "__tag__")


def test_single_param():
    with when:
        class SingleParamScenario(Scenario):
            @params("Bob")
            def __init__(self, user):
                self.user = user

    with then:
        scenarios = get_scenarios("SingleParamScenario", globals())
        assert len(scenarios) == 1
        assert issubclass(scenarios[0], Scenario)


def test_multiple_params():
    with when:
        class MultipleParamsScenario(Scenario):
            @params("Bob")
            @params("Alice")
            def __init__(self, user):
                self.user = user

    with then:
        scenarios = get_scenarios("MultipleParamsScenario", globals())
        assert len(scenarios) == 2
        assert issubclass(scenarios[0], Scenario)
        assert issubclass(scenarios[1], Scenario)


# pytest.mark.skipif does not work as expected
# Also global "if sys.version_info >= (3, 9)" does not work as expected with pytest
# (SyntaxError: invalid syntax)
if sys.version_info < (3, 9):
    params_decorator = cast(Any, params)
else:
    params_decorator = cast(Any, params)
    params_decorator_py39 = linesep.join([
        "def params_decorator(decorators, args, kwargs):",
        "    return params[decorators](*args, **kwargs)",
    ])
    code_object = compile(params_decorator_py39, "<string>", "exec")
    exec(code_object)


@pytest.mark.skipif(sys.version_info < (3, 9), reason="requires python3.9 or higher")
def test_proxy_param():
    print("test_proxy_param")
    with when:
        class ProxyParamScenario(Scenario):
            @params_decorator((label("label"), tag("tag")), ("Bob",), {})
            def __init__(self, user):
                self.user = user

    with then:
        scenarios = get_scenarios("ProxyParamScenario", globals())
        assert len(scenarios) == 1

        assert issubclass(scenarios[0], Scenario)
        assert getattr(scenarios[0], "__label__") == "label"
        assert getattr(scenarios[0], "__tag__") == "tag"


@pytest.mark.skipif(sys.version_info < (3, 9), reason="requires python3.9 or higher")
def test_proxy_params():
    with when:
        class ProxyParamsScenario(Scenario):
            @params_decorator((label("label1"),), ("Bob",), {})
            @params_decorator((label("label2"),), ("Alice",), {})
            def __init__(self, user):
                self.user = user

    with then:
        scenarios = get_scenarios("ProxyParamsScenario", globals())
        assert len(scenarios) == 2

        assert issubclass(scenarios[0], Scenario)
        assert getattr(scenarios[0], "__label__") == "label1"
        assert issubclass(scenarios[1], Scenario)
        assert getattr(scenarios[1], "__label__") == "label2"
