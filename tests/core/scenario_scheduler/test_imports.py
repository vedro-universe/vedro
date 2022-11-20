from importlib import import_module

from baby_steps import then, when


# moved vedro.core._scenario_scheduler -> vedro.core.scenario_scheduler
# in v1.8
def test_backward_compatibility():
    with when:
        module = import_module("vedro.core._scenario_scheduler")

    with then:
        assert module.ScenarioScheduler
        assert module.MonotonicScenarioScheduler
