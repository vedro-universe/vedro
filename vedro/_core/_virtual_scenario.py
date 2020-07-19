import inspect
import os
from typing import Any, Generator, List, Type, Union

from .._scenario import Scenario
from ._virtual_step import VirtualStep


class ScenarioStatus:
    PASSED = "PASSED"
    FAILED = "FAILED"
    SKIPPED = "SKIPPED"


class VirtualScenario:
    def __init__(self, scenario: Type[Scenario]) -> None:
        self._scenario: Type[Scenario] = scenario
        self._status: Union[str, None] = None
        self._path: str = inspect.getfile(scenario)
        self._steps: List[VirtualStep] = []
        self._errors: List[str] = []
        self._exception: Any = None
        self._scope: Union[Scenario, None] = None
        for step in self._scenario.__dict__:
            if not step.startswith("_"):
                method = getattr(self._scenario, step)
                if inspect.isfunction(method):
                    self._steps.append(VirtualStep(method))

    @property
    def subject(self) -> Any:
        return getattr(self._scenario, "subject", None)

    @property
    def path(self) -> str:
        return self._path

    @property
    def namespace(self) -> str:
        return os.path.dirname(os.path.relpath(self._path, "scenarios"))

    @property
    def filename(self) -> str:
        basename = os.path.basename(self._path)
        filename, _ = os.path.splitext(basename)
        return filename

    @property
    def errors(self) -> List[str]:
        return self._errors

    @property
    def exception(self) -> Any:
        return self._exception

    @property
    def scenario(self) -> Type[Scenario]:
        return self._scenario

    @property
    def scope(self) -> Union[Scenario, None]:
        return self._scope

    def set_scope(self, scope: Scenario) -> None:
        self._scope = scope

    def set_errors(self, errors: List[Any]) -> None:
        self._errors = errors

    def set_exception(self, exception: Any) -> None:
        self._exception = exception

    def get_steps(self) -> Generator[VirtualStep, None, None]:
        for step in self._steps:
            yield step

    def __call__(self) -> Any:
        return self._scenario()

    def mark_passed(self) -> None:
        self._status = ScenarioStatus.PASSED

    def is_passed(self) -> bool:
        return self._status == ScenarioStatus.PASSED

    def mark_failed(self) -> None:
        self._status = ScenarioStatus.FAILED

    def is_failed(self) -> bool:
        return self._status == ScenarioStatus.FAILED

    def mark_skipped(self) -> None:
        self._status = ScenarioStatus.SKIPPED

    def is_skipped(self) -> bool:
        return self._status == ScenarioStatus.SKIPPED
