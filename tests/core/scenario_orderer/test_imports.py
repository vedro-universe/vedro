from importlib import import_module

from baby_steps import then, when


# moved vedro.core._scenario_orderer -> vedro.core.scenario_orderer
# in v1.8
def test_backward_compatibility():
    with when:
        module = import_module("vedro.core._scenario_orderer")

    with then:
        assert module.ScenarioOrderer
        assert module.PlainScenarioOrderer
