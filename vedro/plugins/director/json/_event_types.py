from typing import List, Optional, TypedDict, Union

__all__ = ("StartupEventDict", "ScenarioEventDict", "ScenarioReportedEventDict",
           "CleanupEventDict", "EventDict", "ExcInfoDict", "ScenarioDict", "StepDict",)


class EventDict(TypedDict):
    """
    Represents the minimal event header.

    Provides the event kind and the time it was created. Extended event
    payloads inherit from this base.
    """

    event: str
    """
    Event name or identifier (e.g., ``"startup"``, ``"scenario"``, ``"cleanup"``).
    """

    timestamp: int
    """
    Event creation time as an integer timestamp (Unix epoch based).
    """


class ExcInfoDict(TypedDict):
    """
    Carries structured exception information.

    Supplies key details for error reporting and debugging.
    """

    type: str
    """
    Exception class name or symbolic identifier.
    """

    message: str
    """
    Human-readable message describing the exception.
    """

    file: Optional[str]
    """
    Source file path where the exception originates, if available.
    """

    lineno: Optional[int]
    """
    Line number in the source file where the exception occurs, if available.
    """


class DiscoveryStatsDict(TypedDict):
    """
    Summarizes discovery results prior to execution.
    """

    discovered: int
    """
    Number of scenarios found during discovery.
    """

    scheduled: int
    """
    Number of scenarios skipped.
    """

    skipped: int
    """
    Number of scenarios excluded from execution.
    """


class ScenarioDict(TypedDict):
    """
    Describes a single scenario and its execution outcome.
    """

    id: str
    """
    Stable identifier for the scenario.
    """

    subject: str
    """
    Human-readable title or subject of the scenario.
    """

    path: str
    """
    Filesystem or module path where the scenario is defined.
    """

    lineno: Union[int, None]
    """
    Line number of the scenario definition, or ``None`` if unavailable.
    """

    status: str
    """
    Execution outcome/status (e.g., ``"passed"``, ``"failed"``, ``"skipped"``).
    """

    elapsed: int
    """
    Scenario execution duration as an integer time value.
    """

    skip_reason: Optional[str]
    """
    Explanation for skipping the scenario, if applicable.
    """


class StepDict(TypedDict):
    """
    Details a single step within a scenario execution.
    """

    name: str
    """
    Step name or label.
    """

    status: str
    """
    Step outcome/status (e.g., ``"passed"``, ``"failed"``).
    """

    elapsed: int
    """
    Step execution duration as an integer time value.
    """

    error: Optional[ExcInfoDict]
    """
    Exception information if the step fails, otherwise ``None``.
    """


class ReportDict(TypedDict):
    """
    Aggregates final run statistics across all scenarios.
    """

    total: int
    """
    Total number of scenarios considered in the run.
    """

    passed: int
    """
    Number of scenarios that passed.
    """

    failed: int
    """
    Number of scenarios that failed.
    """

    skipped: int
    """
    Number of scenarios that were skipped.
    """

    elapsed: int
    """
    Total execution duration for the run as an integer time value.
    """

    interrupted: Optional[ExcInfoDict]
    """
    Exception information if the run was interrupted prematurely, otherwise ``None``.
    """


class StartupEventDict(EventDict):
    """
    Event emitted at startup with discovery statistics.
    """

    scenarios: DiscoveryStatsDict
    """
    Discovery statistics captured at startup.
    """

    rich_output: Optional[str]
    """
    Pre-rendered terminal output captured from the rich reporter, if available.
    """


class ScenarioEventDict(EventDict):
    """
    Event describing a scenario state change or progress update.
    """

    scenario: ScenarioDict
    """
    Scenario payload associated with the event.
    """

    rich_output: Optional[str]
    """
    Pre-rendered terminal output captured from the rich reporter, if available.
    """


class ScenarioReportedEventDict(EventDict):
    """
    Event carrying the final per-scenario report including steps.
    """

    scenario: ScenarioDict
    """
    Scenario payload containing final status and timing.
    """

    steps: List[StepDict]
    """
    Ordered list of step results for the scenario.
    """

    rich_output: Optional[str]
    """
    Pre-rendered terminal output captured from the rich reporter, if available.
    """


class CleanupEventDict(EventDict):
    """
    Event emitted during cleanup with the aggregate run report.
    """

    report: ReportDict
    """
    Final aggregate report summarizing the run.
    """

    rich_output: Optional[str]
    """
    Pre-rendered terminal output captured from the rich reporter, if available.
    """
