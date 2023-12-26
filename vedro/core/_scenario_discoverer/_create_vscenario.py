import inspect
from typing import Type

from ..._scenario import Scenario
from .._virtual_scenario import VirtualScenario
from .._virtual_step import VirtualStep

__all__ = ("create_vscenario",)


def create_vscenario(scenario: Type[Scenario]) -> VirtualScenario:
    """
    Creates a VirtualScenario from a given Scenario class.

    This function inspects the given Scenario class, extracts its methods that represent
    steps, and constructs a VirtualScenario object that encapsulates the scenario and its steps.
    It skips private methods (those starting with '_') and only includes functions.

    :param scenario: The Scenario class to be converted into a VirtualScenario.
    :return: A VirtualScenario object containing the scenario and its steps.
    """
    steps = []
    for step in scenario.__dict__:
        if step.startswith("_"):
            continue
        method = getattr(scenario, step)
        if not inspect.isfunction(method):
            continue
        steps.append(VirtualStep(method))
    return VirtualScenario(scenario, steps)
