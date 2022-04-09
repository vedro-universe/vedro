import os
from hashlib import blake2b
from inspect import BoundArguments
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
    def template_total(self) -> Union[int, None]:
        idx = getattr(self._orig_scenario, "__vedro__template_total__", None)
        return cast(Union[int, None], idx)

    @property
    def template_args(self) -> Union[BoundArguments, None]:
        args = getattr(self._orig_scenario, "__vedro__template_args__", None)
        return cast(Union[BoundArguments, None], args)

    @property
    def path(self) -> Path:
        return self._path

    @property
    def subject(self) -> str:
        subject = getattr(self._orig_scenario, "subject", None)
        if not isinstance(subject, str) or subject.strip() == "":
            subject = self._path.stem.replace("_", " ")

        if self.template_args:
            subject = subject.format(**self.template_args.arguments)
        return subject

    @property
    def namespace(self) -> str:
        module = self._orig_scenario.__module__
        rel_path = os.path.relpath(self._path, module.split(".")[0])
        return os.path.dirname(rel_path)

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
