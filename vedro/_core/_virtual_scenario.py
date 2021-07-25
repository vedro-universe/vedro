from hashlib import blake2b
from pathlib import Path
from typing import Any, List, Type, Union, cast

from .._scenario import Scenario
from ._virtual_step import VirtualStep

__all__ = ("VirtualScenario",)


class VirtualScenario:
    def __init__(self, orig_scenario: Type[Scenario], steps: List[VirtualStep]) -> None:
        self._orig_scenario = orig_scenario
        self._steps = steps
        self._path = Path(getattr(orig_scenario, "__file__", "."))
        self._is_skipped = False

    @property
    def steps(self) -> List[VirtualStep]:
        return self._steps

    @property
    def unique_id(self) -> str:
        unique_name = f"{self._path}::{self._orig_scenario.__qualname__}"
        return blake2b(unique_name.encode(), digest_size=20).hexdigest()

    @property
    def template_index(self) -> Union[int, None]:
        idx = getattr(self._orig_scenario, "__vedro__template_index__", None)
        return cast(Union[int, None], idx)

    @property
    def path(self) -> Path:
        return self._path

    @property
    def subject(self) -> Union[str, None]:
        return cast(Union[str, None], getattr(self._orig_scenario, "subject", None))

    def skip(self) -> None:
        self._is_skipped = True

    def is_skipped(self) -> bool:
        return self._is_skipped

    def __call__(self) -> Scenario:
        return self._orig_scenario()

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self._orig_scenario!r}, {self._steps!r})"

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, self.__class__) and (self.__dict__ == other.__dict__)
