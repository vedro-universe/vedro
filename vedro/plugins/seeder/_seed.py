from inspect import isclass
from os import linesep
from typing import Callable, Optional, Type, TypeVar, cast

from vedro._scenario import Scenario
from vedro.core import set_scenario_meta

from ._seeder import SeederPlugin

__all__ = ("seed",)


T = TypeVar("T", bound=Scenario)


def seed(seed_value: str, *,
         use_fixed_seed: Optional[bool] = None) -> Callable[[Type[T]], Type[T]]:
    """
    Set a custom seed for a Vedro scenario, optionally specifying fixed seed behavior.

    This decorator allows you to override the global seed settings for individual scenarios,
    providing fine-grained control over the random behavior in specific test scenarios.

    Usage examples:

    cls-based:
        @seed("custom-seed-123")
        class Scenario(vedro.Scenario):
            ...

        @seed("custom-seed-456", use_fixed_seed=True)
        class Scenario(vedro.Scenario):
            ...

    fn-based:
        @scenario[seed("custom-seed-123")]()
        def subject():
            ...

        @scenario[seed("custom-seed-456", use_fixed_seed=True)]()
        def subject():
            ...

    :param seed_value: The seed value to use for this scenario.
    :param use_fixed_seed: Whether to use the same seed for repeated runs of this scenario
                          within the same test execution. If None, falls back to global setting.
    :return: A decorator that applies the seed configuration to the scenario.
    :raises TypeError: If used on a non-Scenario class.
    """
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

        if use_fixed_seed is not None:
            set_scenario_meta(scn, key="use_fixed_seed", value=use_fixed_seed, plugin=SeederPlugin)

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
