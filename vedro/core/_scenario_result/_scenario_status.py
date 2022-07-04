from enum import Enum

__all__ = ("ScenarioStatus",)


class ScenarioStatus(Enum):
    PENDING = "PENDING"
    PASSED = "PASSED"
    FAILED = "FAILED"
    SKIPPED = "SKIPPED"
