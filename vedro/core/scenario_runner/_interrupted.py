from .._exc_info import ExcInfo
from .._scenario_result import ScenarioResult
from .._step_result import StepResult

__all__ = ("Interrupted", "StepInterrupted", "ScenarioInterrupted", "RunInterrupted")


class Interrupted(BaseException):
    pass


class StepInterrupted(Interrupted):
    def __init__(self, exc_info: ExcInfo, step_result: StepResult) -> None:
        self._exc_info = exc_info
        self._step_result = step_result

    @property
    def exc_info(self) -> ExcInfo:
        return self._exc_info

    @property
    def step_result(self) -> StepResult:
        return self._step_result

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self._exc_info!r}, {self._step_result!r})"


class ScenarioInterrupted(Interrupted):
    def __init__(self, exc_info: ExcInfo, scenario_result: ScenarioResult) -> None:
        self._exc_info = exc_info
        self._scenario_result = scenario_result

    @property
    def exc_info(self) -> ExcInfo:
        return self._exc_info

    @property
    def scenario_result(self) -> ScenarioResult:
        return self._scenario_result

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self._exc_info!r}, {self._scenario_result!r})"


class RunInterrupted(Interrupted):
    def __init__(self, exc_info: ExcInfo) -> None:
        self._exc_info = exc_info

    @property
    def exc_info(self) -> ExcInfo:
        return self._exc_info

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self._exc_info!r})"
