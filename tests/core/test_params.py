from functools import partial
from typing import List, Type

from baby_steps import given, then, when

from vedro import Scenario, params


def get_scenarios(key: str) -> List[Type[Scenario]]:
    return [scn for name, scn in globals().items() if name.startswith(key)]


def labeled(key, value):
    def wrapped(fn):
        setattr(fn, key, value)
        return fn
    return wrapped


label = partial(labeled, "__label__")
tag = partial(labeled, "__tag__")


def test_single_param():
    with given:
        class SingleParamScenario(Scenario):
            @params("Bob")
            def __init__(self, user):
                self.user = user

    with when:
        scenarios = get_scenarios("SingleParamScenario")

    with then:
        assert len(scenarios) == 1
        assert issubclass(scenarios[0], Scenario)


def test_multiple_params():
    with given:
        class MultipleParamsScenario(Scenario):
            @params("Bob")
            @params("Alice")
            def __init__(self, user):
                self.user = user

    with when:
        scenarios = get_scenarios("MultipleParamsScenario")

    with then:
        assert len(scenarios) == 2
        assert issubclass(scenarios[0], Scenario)
        assert issubclass(scenarios[1], Scenario)


def test_proxy_param():
    with given:
        class ProxyParamScenario(Scenario):
            @params[label("label"), tag("tag")]("Bob")
            def __init__(self, user):
                self.user = user

    with when:
        scenarios = get_scenarios("ProxyParamScenario")

    with then:
        assert len(scenarios) == 1
        assert issubclass(scenarios[0], Scenario)
        assert getattr(scenarios[0], "__label__") == "label"
        assert getattr(scenarios[0], "__tag__") == "tag"


def test_proxy_params():
    with given:
        class ProxyParamsScenario(Scenario):
            @params[label("label1")]("Bob")
            @params[label("label2")]("Alice")
            def __init__(self, user):
                self.user = user

    with when:
        scenarios = get_scenarios("ProxyParamsScenario")

    with then:
        assert len(scenarios) == 2
        assert issubclass(scenarios[0], Scenario)
        assert getattr(scenarios[0], "__label__") == "label1"
        assert issubclass(scenarios[1], Scenario)
        assert getattr(scenarios[1], "__label__") == "label2"
