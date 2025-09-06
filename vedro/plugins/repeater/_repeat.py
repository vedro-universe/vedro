from inspect import isclass
from os import linesep
from typing import Callable, List, Optional, Tuple, Type, TypeVar, Union, cast

from vedro._scenario import Scenario
from vedro.core import set_scenario_meta

__all__ = ("repeat", "_repeat_queue",)


T = TypeVar("T", bound=Scenario)

DelayType = Union[int, float]
_repeat_queue: List[Tuple[int, Union[DelayType, None]]] = []


def repeat(times: int, *, delay: Optional[DelayType] = None) -> Callable[[Type[T]], Type[T]]:
    """
    Set custom repetition configuration for a Vedro scenario.

    This decorator allows you to override the global repetition settings for individual
    scenarios, providing fine-grained control over test execution frequency and timing.

    Usage examples:

    cls-based:
        @repeat(3, delay=1.0)
        class Scenario(vedro.Scenario):
            ...

    fn-based:
        @scenario[repeat(5)]()
        def subject():
            ...

    :param times: The number of times to repeat the scenario (must be >= 1).
    :param delay: The delay in seconds between repetitions (must be >= 0.0 when provided).
    :return: A decorator that applies the repetition configuration to the scenario.
    :raises ValueError: If times < 1 or delay < 0.0.
    :raises TypeError: If used on a non-Scenario class.
    """
    if not isinstance(times, int):
        raise TypeError(f"times must be an integer, got {type(times).__name__}")
    if times < 1:
        raise ValueError(f"times must be >= 1, got {times}")

    if delay is not None:
        if not isinstance(delay, (int, float)):
            raise TypeError(f"delay must be an int or float, got {type(delay).__name__}")
        if delay < 0.0:
            raise ValueError(f"delay must be >= 0.0, got {delay}")

    _repeat_queue.append((times, delay))

    def apply_repeat(scn: Type[T]) -> Type[T]:
        """
        Apply repetition metadata to the scenario for controlled test execution.

        :param scn: Scenario class to apply the repetition configuration to.
        :return: The same scenario class with updated metadata.
        :raises TypeError: If the argument is not a subclass of Scenario.
        """
        if not isclass(scn) or not issubclass(scn, Scenario):
            raise TypeError(_format_repeat_usage_error(times, delay))

        from ._repeater import RepeaterPlugin  # To avoid circular import
        set_scenario_meta(scn, key="repeats", value=times, plugin=RepeaterPlugin)
        if delay is not None:
            set_scenario_meta(scn, key="repeats_delay", value=delay, plugin=RepeaterPlugin)

        return cast(Type[T], scn)

    return apply_repeat


def _format_repeat_usage_error(times: int, delay: Optional[DelayType] = None) -> str:
    """
    Format an error message explaining correct usage of the @repeat decorator.

    :param times: The times value provided to the decorator.
    :param delay: The delay value provided to the decorator.
    :return: A usage error message with examples for both class-based and function-based scenarios.
    """
    delay_str = f", delay={delay}" if delay else ""
    return linesep.join([
        "Decorator @repeat can be used only with Vedro scenarios:",
        "",
        "cls-based:",
        f"    @repeat({times}{delay_str})",
        "    class Scenario(vedro.Scenario):",
        "        ...",
        "",
        "fn-based:",
        f"    @scenario[repeat({times}{delay_str})]()",
        "    def subject():",
        "        ...",
    ])
