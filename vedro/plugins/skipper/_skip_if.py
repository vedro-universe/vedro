from inspect import isclass
from os import linesep
from typing import Any, Callable, Optional, Type, TypeVar, cast

from vedro._scenario import Scenario

from ._skip import skip

__all__ = ("skip_if",)


T = TypeVar("T", bound=Scenario)


def skip_if(
    cond: Callable[[], bool], reason: Optional[str] = None
) -> Callable[[Type[T]], Type[T]]:
    """
    Exclude a scenario from execution if a condition evaluates to True.

    Can be used to dynamically skip scenarios. An optional reason can be provided to explain
    why the scenario is being skipped, which helps improve test reporting and maintainability.

    Usage examples:

    cls-based:
        @skip_if(lambda: True, "Not implemented")
        class Scenario(vedro.Scenario):
            ...

    fn-based:
        @scenario[skip_if(lambda: True, "Not implemented")]
        def subject():
            ...

    :param cond: A callable that returns a boolean indicating whether to skip the scenario.
    :param reason: Optional string describing the reason for skipping.
    :return: A decorator that conditionally excludes the scenario from execution.
    :raises TypeError: If `cond` is not callable or the decorator is applied to a non-Scenario
                       class.

    For more details and examples, see:
    https://vedro.io/docs/features/skipping-scenarios
    """
    if isinstance(cond, type) or not callable(cond):
        raise TypeError(_format_skip_if_usage_error(reason))

    def apply_skip_if(scenario: Type[T]) -> Type[T]:
        """
        Apply the skip decorator if the condition evaluates to True.

        :param scenario: Scenario class to be conditionally excluded.
        :return: The same scenario class, optionally decorated with `skip`.
        :raises TypeError: If applied to a non-Scenario class.
        """
        if not isclass(scenario) or not issubclass(scenario, Scenario):
            raise TypeError(_format_skip_if_usage_error(reason))
        if cond():
            decorator = skip(reason) if reason is not None else skip()
            return decorator(cast(Type[T], scenario))
        else:
            return cast(Type[T], scenario)

    return apply_skip_if


def _format_skip_if_usage_error(maybe_reason: Any) -> str:
    """
    Generate a usage error message for incorrect use of the @skip_if decorator.

    :param maybe_reason: The optional reason provided to the decorator.
    :return: A formatted usage message with examples for correct usage.
    """
    if maybe_reason is not None:
        decorator_repr = f"skip_if(<cond>, {maybe_reason!r})"
    else:
        decorator_repr = "skip_if(<cond>)"

    return linesep.join([
        "Decorator @skip_if must be used as @skip_if(<condition>, 'reason?') "
        "and only with Vedro scenarios:",
        "",
        "cls-based:",
        f"    @{decorator_repr}",
        "    class Scenario(vedro.Scenario):",
        "        ...",
        "",
        "fn-based:",
        f"    @scenario[{decorator_repr}]",
        "    def subject():",
        "        ...",
    ])
