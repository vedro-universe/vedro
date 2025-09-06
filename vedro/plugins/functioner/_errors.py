__all__ = ("ScenarioError", "DuplicateScenarioError", "AnonymousScenarioError",)


class ScenarioError(BaseException):
    pass


class DuplicateScenarioError(ScenarioError):
    pass


class AnonymousScenarioError(ScenarioError):
    pass
