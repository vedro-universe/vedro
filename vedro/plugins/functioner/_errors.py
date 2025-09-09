__all__ = ("ScenarioError", "DuplicateScenarioError", "AnonymousScenarioError",
           "FunctionShadowingError",)


class ScenarioError(BaseException):
    pass


class DuplicateScenarioError(ScenarioError):
    pass


class AnonymousScenarioError(ScenarioError):
    pass


class FunctionShadowingError(ScenarioError):
    pass
