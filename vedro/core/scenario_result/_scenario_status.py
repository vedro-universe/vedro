from enum import Enum

__all__ = ("ScenarioStatus",)


class ScenarioStatus(Enum):
    """
    Enumeration of possible states for `ScenarioResult` to indicate the current status
    of a test scenario.

    For more information, refer to https://vedro.io/docs/core/scenario-status.
    """

    # Indicates the scenario is queued and waiting for execution.
    PENDING = "PENDING"

    # Signifies the scenario has completed successfully with all assertions validated.
    PASSED = "PASSED"

    # Marks the scenario as unsuccessful due to failed assertions or unexpected errors.
    FAILED = "FAILED"

    # Represents scenarios that are deliberately not executed.
    SKIPPED = "SKIPPED"
