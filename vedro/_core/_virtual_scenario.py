from pathlib import Path
from typing import Any, List, Type, Union

from .._scenario import Scenario
from ._virtual_step import VirtualStep

__all__ = ("VirtualScenario",)


class VirtualScenario:
    def __init__(self, orig_scenario: Type[Scenario], steps: List[VirtualStep]) -> None:
        self._orig_scenario = orig_scenario
        self._steps = steps
        self._path = Path(getattr(orig_scenario, "__file__"))

    @property
    def steps(self) -> List[VirtualStep]:
        return self._steps

    @property
    def path(self) -> Path:
        return self._path

    @property
    def subject(self) -> Union[str, None]:
        return getattr(self._orig_scenario, "subject", None)

    def is_skipped(self) -> bool:
        return False

    def __call__(self) -> Scenario:
        return self._orig_scenario()

    def __repr__(self) -> str:
        return f"VirtualScenario({self._path!r}, {self._steps!r})"

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, self.__class__) and self.__dict__ == other.__dict__
