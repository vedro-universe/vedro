__all__ = ("ScenarioDeclarationError", "DuplicateScenarioError", "AnonymousScenarioError",
           "FunctionShadowingError",)


class ScenarioDeclarationError(BaseException):
    """
    Base exception for scenario-related errors.

    This is the base class for all exceptions raised by the functioner plugin
    when dealing with scenario creation and validation.
    """
    pass


class DuplicateScenarioError(ScenarioDeclarationError):
    """
    Raised when attempting to create a scenario with a duplicate name.

    This occurs when:
    - Two scenario functions have the same name
    - Two anonymous scenarios have the same subject
    - A scenario name conflicts with an existing scenario
    """
    pass


class AnonymousScenarioError(ScenarioDeclarationError):
    """
    Raised when there's an issue with an anonymous scenario function.

    This typically occurs when an anonymous function (named '_') is used
    without providing a subject for the scenario.
    """
    pass


class FunctionShadowingError(ScenarioDeclarationError):
    """
    Raised when a scenario would shadow an existing non-scenario function.

    This prevents scenarios from accidentally overwriting existing functions
    in the module namespace, which could lead to unexpected behavior.
    """
    pass
