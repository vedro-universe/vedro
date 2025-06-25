from inspect import isclass
from os import linesep
from typing import Callable, Type, TypeVar, Union, cast, overload

from vedro._scenario import Scenario
from vedro.core import set_scenario_meta

from ._skipper import SkipperPlugin

__all__ = ("only",)

T = TypeVar("T", bound=Scenario)


@overload
def only(scenario: Type[T]) -> Type[T]:
    """
    Enable usage as `@only` to designate a scenario for exclusive execution.

    :param scenario: The scenario class to be designated as the only one to run.
    :return: The same scenario class, flagged for exclusive execution.
    """
    pass


@overload
def only() -> Callable[[Type[T]], Type[T]]:
    """
    Enable usage as `@only()` to return a decorator.

    :return: A decorator that designates a scenario for exclusive execution.
    """
    pass


def only(scenario: Union[Type[T], None] = None) -> Union[Type[T], Callable[[Type[T]], Type[T]]]:
    """
    Designate a Vedro scenario class to be the only one selected for execution.

    Can be used with or without parentheses: `@only` or `@only()`.

    Usage examples:

    cls-based:
        @only
        class Scenario(vedro.Scenario):
            ...

    fn-based:
        @scenario[only]()
        def subject():
            ...

    :param scenario: Scenario class to decorate, or None if used as @only().
    :return: Decorated scenario class or a decorator.
    :raises TypeError: If used on a non-Scenario class.

    For more details and examples, see:
    https://vedro.io/docs/basics/selecting-and-ignoring
    """

    def apply_only(scn: Type[T]) -> Type[T]:
        """
        Apply metadata indicating that this scenario should be the only one executed.

        :param scn: Scenario class to designate for exclusive execution.
        :return: The same scenario class with updated metadata.
        :raises TypeError: If the argument is not a subclass of Scenario.
        """
        if not isclass(scn) or not issubclass(scn, Scenario):
            raise TypeError(_format_only_usage_error())

        set_scenario_meta(scn, key="only", value=True, plugin=SkipperPlugin,
                          fallback_key="__vedro__only__")

        return cast(Type[T], scn)

    # When used with parentheses (e.g., @only()), return the decorator function
    if scenario is None:
        return apply_only
    # When used without parentheses (e.g., @only), apply the decorator immediately
    return apply_only(scenario)


def _format_only_usage_error() -> str:
    """
    Format an error message explaining correct usage of the @only decorator.

    :return: A usage error message with examples for both class-based and function-based scenarios.
    """
    return linesep.join([
        "Decorator @only can be used only with Vedro scenarios:",
        "",
        "cls-based:",
        "    @only",
        "    class Scenario(vedro.Scenario):",
        "        ...",
        "",
        "fn-based:",
        "    @scenario[only]()",
        "    def subject():",
        "        ...",
    ])
