import os
from hashlib import blake2b
from inspect import BoundArguments
from pathlib import Path
from typing import Any, List, Optional, Type, Union, cast

from .._scenario import Scenario
from ._virtual_step import VirtualStep

__all__ = ("VirtualScenario", "ScenarioInitError",)


class ScenarioInitError(Exception):
    pass


class VirtualScenario:
    def __init__(self, orig_scenario: Type[Scenario], steps: List[VirtualStep]) -> None:
        self._orig_scenario = orig_scenario
        self._steps = steps
        self._path = Path(getattr(orig_scenario, "__file__", "."))
        self._is_skipped = False
        self._skip_reason: Union[str, None] = None

    @property
    def steps(self) -> List[VirtualStep]:
        return self._steps

    @property
    def unique_id(self) -> str:
        unique_id = f"{self.rel_path}::{self.name}"
        if self.template_index is not None:
            unique_id += f"#{self.template_index}"
        return unique_id

    @property
    def unique_hash(self) -> str:
        return blake2b(self.unique_id.encode(), digest_size=20).hexdigest()

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
    def rel_path(self) -> Path:
        return self._path.relative_to(Path.cwd())

    @property
    def name(self) -> str:
        return getattr(self._orig_scenario, "__vedro__template_name__",
                       self._orig_scenario.__name__)

    @property
    def subject(self) -> str:
        subject = getattr(self._orig_scenario, "subject", None)
        if not isinstance(subject, str) or subject.strip() == "":
            subject = self._path.stem.replace("_", " ")

        if not self.template_args:
            return subject

        try:
            return subject.format(**self.template_args.arguments)
        except Exception as exc:
            message = f'Can\'t format subject "{subject}" at "{self.rel_path}" ({exc})'
            raise ValueError(message) from None

    @property
    def namespace(self) -> str:
        module = self._orig_scenario.__module__
        rel_path = os.path.relpath(self._path, module.split(".")[0])
        return os.path.dirname(rel_path)

    def skip(self, reason: Optional[str] = None) -> None:
        self._is_skipped = True
        if reason:
            self._skip_reason = reason

    @property
    def skip_reason(self) -> Optional[str]:
        return self._skip_reason

    def is_skipped(self) -> bool:
        return self._is_skipped

    def __call__(self) -> Scenario:
        try:
            return self._orig_scenario()
        except Exception as exc:
            message = f'Can\'t initialize scenario "{self.subject}" at "{self.rel_path}" ({exc!r})'
            raise ScenarioInitError(message) from None

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} {str(self.rel_path)!r}>"

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, self.__class__) and (self.__dict__ == other.__dict__)
