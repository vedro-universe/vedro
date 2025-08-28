from typing import List, Optional, TypedDict, Union

__all__ = ("StartupEventDict", "ScenarioEventDict", "ScenarioReportedEventDict",
           "CleanupEventDict", "EventDict", "ExcInfoDict", "ScenarioDict", "StepDict",)


class EventDict(TypedDict):
    event: str
    timestamp: int


class ExcInfoDict(TypedDict):
    type: str
    message: str
    file: Optional[str]
    lineno: Optional[int]


class DiscoveryStatsDict(TypedDict):
    discovered: int
    scheduled: int
    skipped: int


class ScenarioDict(TypedDict):
    id: str
    subject: str
    path: str
    lineno: Union[int, None]
    status: str
    elapsed: int
    skip_reason: Optional[str]


class StepDict(TypedDict):
    name: str
    status: str
    elapsed: int
    error: Optional[ExcInfoDict]


class ReportDict(TypedDict):
    total: int
    passed: int
    failed: int
    skipped: int
    elapsed: int
    interrupted: Optional[ExcInfoDict]


class StartupEventDict(EventDict):
    scenarios: DiscoveryStatsDict
    rich_output: Optional[str]


class ScenarioEventDict(EventDict):
    scenario: ScenarioDict
    rich_output: Optional[str]


class ScenarioReportedEventDict(EventDict):
    scenario: ScenarioDict
    steps: List[StepDict]
    rich_output: Optional[str]


class CleanupEventDict(EventDict):
    report: ReportDict
    rich_output: Optional[str]
