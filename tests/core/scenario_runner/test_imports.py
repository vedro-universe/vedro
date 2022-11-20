from importlib import import_module

from baby_steps import then, when


# moved vedro.core._scenario_runner -> vedro.core.scenario_runner
# in v1.8
def test_backward_compatibility():
    with when:
        module = import_module("vedro.core._scenario_runner")

    with then:
        assert module.ScenarioRunner
        assert module.MonotonicScenarioRunner
