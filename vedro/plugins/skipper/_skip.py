from inspect import isclass
from os import linesep
from typing import Any, Callable, Type, TypeVar, Union, cast, overload

from vedro._scenario import Scenario
from vedro.core import set_scenario_meta

from ._skipper import SkipperPlugin

__all__ = ("skip",)


T = TypeVar("T", bound=Scenario)


@overload
def skip(scenario_or_reason: Type[T]) -> Type[T]:
    """
    Enable usage as `@skip` to exclude a scenario from execution.

    :param scenario_or_reason: The scenario class to be excluded.
    :return: The same scenario class, updated with skip metadata.
    """
    pass


@overload
def skip() -> Callable[[Type[T]], Type[T]]:
    """
    Enable usage as `@skip()` to return a decorator.

    :return: A decorator that excludes the decorated scenario from execution.
    """
    pass


@overload
def skip(scenario_or_reason: str) -> Callable[[Type[T]], Type[T]]:
    """
    Enable usage as `@skip("reason")` to exclude a scenario with a reason.

    :param scenario_or_reason: A string describing why the scenario is skipped.
    :return: A decorator that excludes the scenario and stores the reason.
    """
    pass


def skip(
    scenario_or_reason: Union[Type[T], str, None] = None
) -> Union[Type[T], Callable[[Type[T]], Type[T]]]:
    """
    Exclude a scenario class from execution, optionally providing a reason.

    Can be used as `@skip`, `@skip()`, or `@skip("reason")`.

    Usage examples:

    cls-based:
        @skip
        class Scenario(vedro.Scenario):
            ...

    fn-based:
        @scenario[skip]()
        def subject():
            ...

    :param scenario_or_reason: Scenario class to decorate, a reason string,
                               or None if used as @skip().
    :return: Decorated scenario class or a decorator.
    :raises TypeError: If applied to a non-Scenario class.

    For more details and examples, see:
    https://vedro.io/docs/features/skipping-scenarios
    """

    def apply_skip(scn: Type[T]) -> Type[T]:
        """
        Apply skip metadata to a scenario class.

        :param scn: Scenario class to exclude from execution.
        :return: The same scenario class with skip metadata applied.
        :raises TypeError: If the class is not a subclass of Scenario.
        """
        if not isclass(scn) or not issubclass(scn, Scenario):
            raise TypeError(_format_skip_usage_error(scenario_or_reason))

        set_scenario_meta(scn, key="skipped", value=True, plugin=SkipperPlugin,
                          fallback_key="__vedro__skipped__")

        if isinstance(reason := scenario_or_reason, str):
            set_scenario_meta(scn, key="skip_reason", value=reason, plugin=SkipperPlugin,
                              fallback_key="__vedro__skip_reason__")

        return cast(Type[T], scn)

    # When used with or without a reason string (e.g., @skip() or @skip("reason")),
    # return the decorator function for later application.
    if (scenario_or_reason is None) or isinstance(scenario_or_reason, str):
        return apply_skip
    # When used without parentheses (e.g., @skip),
    # apply the decorator immediately to the provided scenario class.
    return apply_skip(scenario_or_reason)


def _format_skip_usage_error(maybe_reason: Any) -> str:
    """
    Generate a usage error message for incorrect usage of the @skip decorator.

    :param maybe_reason: The provided argument to the decorator (could be a reason string).
    :return: A formatted usage string with correct decorator examples.
    """
    if isinstance(maybe_reason, str):
        decorator_repr = f"skip({maybe_reason!r})"
        fn_decorator_repr = f"scenario[{decorator_repr}]"
    else:
        decorator_repr = "skip"
        fn_decorator_repr = f"scenario[{decorator_repr}]()"

    return linesep.join([
        "Decorator @skip can be used only with Vedro scenarios:",
        "",
        "cls-based:",
        f"    @{decorator_repr}",
        "    class Scenario(vedro.Scenario):",
        "        ...",
        "",
        "fn-based:",
        f"    @{fn_decorator_repr}",
        "    def subject():",
        "        ...",
    ])
