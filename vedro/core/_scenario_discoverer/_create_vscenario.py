import inspect
from typing import Type

from ..._scenario import Scenario
from .._virtual_scenario import VirtualScenario
from .._virtual_step import VirtualStep

__all__ = ("create_vscenario",)


def create_vscenario(scenario: Type[Scenario]) -> VirtualScenario:
    steps = []
    for step in scenario.__dict__:
        if step.startswith("_"):
            continue
        method = getattr(scenario, step)
        if not inspect.isfunction(method):
            continue
        steps.append(VirtualStep(method))
    return VirtualScenario(scenario, steps)
