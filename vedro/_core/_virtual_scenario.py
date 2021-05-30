from typing import List, Type

from .._scenario import Scenario
from ._virtual_step import VirtualStep

__all__ = ("VirtualScenario",)


class VirtualScenario:
    def __init__(self, scenario: Type[Scenario], steps: List[VirtualStep]) -> None:
        self._scenario = scenario
        self._steps = steps
        self._path: str = getattr(scenario, "__file__")

    @property
    def steps(self) -> List[VirtualStep]:
        return self._steps

    @property
    def path(self) -> str:
        return self._path

    def is_skipped(self) -> bool:
        return False

    def __call__(self) -> Scenario:
        return self._scenario()

    def __repr__(self) -> str:
        return f"VirtualScenario({self._path!r}, {self._steps!r})"
