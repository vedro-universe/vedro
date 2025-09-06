from inspect import isclass
from os import linesep
from typing import Callable, Type, TypeVar, cast

from vedro._scenario import Scenario
from vedro.core import set_scenario_meta

from ._seeder import SeederPlugin

__all__ = ("seed",)


T = TypeVar("T", bound=Scenario)


def seed(seed_value: str) -> Callable[[Type[T]], Type[T]]:
    """
    Set a custom seed for a Vedro scenario, optionally specifying fixed seed behavior.

    This decorator allows you to override the global seed settings for individual scenarios,
    providing fine-grained control over the random behavior in specific test scenarios.

    Usage examples:

    cls-based:
        @seed("custom-seed-123")
        class Scenario(vedro.Scenario):
            ...

    fn-based:
        @scenario[seed("custom-seed-123")]()
        def subject():
            ...

    :param seed_value: The seed value to use for this scenario.
    :return: A decorator that applies the seed configuration to the scenario.
    :raises TypeError: If used on a non-Scenario class.
    """
    if not isinstance(seed_value, str):
        raise TypeError(f"seed_value must be a string, got {type(seed_value).__name__}")

    def apply_seed(scn: Type[T]) -> Type[T]:
        """
        Apply seed metadata to the scenario for deterministic random behavior.

        :param scn: Scenario class to apply the seed configuration to.
        :return: The same scenario class with updated metadata.
        :raises TypeError: If the argument is not a subclass of Scenario.
        """
        if not isclass(scn) or not issubclass(scn, Scenario):
            raise TypeError(_format_seed_usage_error(seed_value))

        set_scenario_meta(scn, key="seed", value=seed_value, plugin=SeederPlugin)

        return cast(Type[T], scn)

    return apply_seed


def _format_seed_usage_error(seed_value: str) -> str:
    """
    Format an error message explaining correct usage of the @seed decorator.

    :param seed_value: The seed value provided to the decorator.
    :return: A usage error message with examples for both class-based and function-based scenarios.
    """
    return linesep.join([
        "Decorator @seed can be used only with Vedro scenarios:",
        "",
        "cls-based:",
        f"    @seed({seed_value!r})",
        "    class Scenario(vedro.Scenario):",
        "        ...",
        "",
        "fn-based:",
        f"    @scenario[seed({seed_value!r})]()",
        "    def subject():",
        "        ...",
    ])
