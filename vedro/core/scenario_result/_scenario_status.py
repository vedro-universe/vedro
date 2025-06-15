from enum import Enum

__all__ = ("ScenarioStatus",)


class ScenarioStatus(Enum):
    """
    Defines the possible states for a `ScenarioResult`.

    This enumeration indicates the current status of a test scenario during or after
    execution. It provides four distinct states to represent the lifecycle of a scenario.
    """

    PENDING = "PENDING"
    """
    Indicates the scenario is queued and waiting for execution.
    """

    PASSED = "PASSED"
    """
    Signifies the scenario has completed successfully with all assertions validated.
    """

    FAILED = "FAILED"
    """
    Marks the scenario as unsuccessful due to failed assertions or unexpected errors.
    """

    SKIPPED = "SKIPPED"
    """
    Represents scenarios that are deliberately not executed.
    """
