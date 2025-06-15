import inspect
from pathlib import Path
from typing import Type

from ..._scenario import Scenario
from .._virtual_scenario import VirtualScenario
from .._virtual_step import VirtualStep

__all__ = ("create_vscenario",)


def create_vscenario(scenario: Type[Scenario], *,
                     project_dir: Path = Path.cwd()) -> VirtualScenario:
    """
    Create a VirtualScenario from a given Scenario class.

    This function inspects the provided Scenario class, extracts its methods that represent
    steps, and constructs a VirtualScenario object encapsulating the scenario and its steps.
    It omits private methods (those starting with '_') and includes only functions.

    :param scenario: The Scenario class to convert into a VirtualScenario.
    :param project_dir: The root directory of the project.
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
    return VirtualScenario(scenario, steps, project_dir=project_dir)

# TODO: Move the create_vscenario method to the ScenarioLoader class in v2.
#       This will allow the ScenarioLoader to be responsible for creating VirtualScenario objects.
