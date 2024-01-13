from importlib import import_module

from baby_steps import then, when


# moved vedro.core._scenario_discoverer -> vedro.core.scenario_discoverer
# in v1.11
def test_backward_compatibility():
    with when:
        module = import_module("vedro.core._scenario_discoverer")

    with then:
        assert module.ScenarioDiscoverer
        assert module.MultiScenarioDiscoverer
        assert module.create_vscenario
