from enum import Enum
from typing import Any, Callable, List, Optional, Sequence, Set, Tuple, Union, overload

from ._scenario_descriptor import ScenarioDescriptor

__all__ = ("scenario", "ScenarioDecorator",)

Tag = Union[str, Enum]
Tags = Union[List[Tag], Tuple[Tag, ...], Set[Tag]]


class ScenarioDecorator:
    """
    Implements a flexible decorator for defining Vedro scenarios.

    This class allows optional chaining of decorators and parameter sets using
    both decorator syntax and callable invocation.
    """

    def __init__(self, decorators: Tuple[Callable[..., Any], ...] = (),
                 params: Tuple[Any, ...] = (),
                 subject: Optional[str] = None,
                 tags: Tags = ()) -> None:
        """
        Initialize the scenario decorator with optional decorators, parameters, subject, and tags.

        :param decorators: A tuple of decorators to apply to the scenario class. Defaults to empty.
        :param params: A tuple of parameter sets for scenario parameterization. Defaults to empty.
        :param subject: An optional custom human-readable subject for the scenario.
        :param tags: Tags to associate with the scenario. Can be a list, tuple, or set
                     of strings or Enums. Defaults to an empty tuple.
        """
        self._decorators = decorators
        self._params = params
        self._subject = subject
        self._tags = tags

    @overload
    def __call__(self) -> "ScenarioDecorator":
        """
        Enable usage as `@scenario()`.

        :return: The scenario decorator instance itself for chaining.
        """
        ...

    @overload
    def __call__(self, fn: Callable[..., Any], /) -> ScenarioDescriptor:
        """
        Enable usage as `@scenario` directly on a function.

        :param fn: The function to decorate as a scenario.
        :return: A ScenarioDescriptor representing the scenario.
        """
        ...

    @overload
    def __call__(self, subject: str, /) -> "ScenarioDecorator":
        """
        Enable usage as `@scenario("subject")` to set custom subject.

        :param subject: A custom human-readable subject for the scenario.
        :return: A new ScenarioDecorator with subject applied.
        """
        ...

    @overload
    def __call__(self, params: Sequence[Any], /) -> "ScenarioDecorator":
        """
        Enable usage as `@scenario(params)` to set parameterization.

        :param params: A sequence of parameter sets for the scenario.
        :return: A new ScenarioDecorator with parameters applied.
        """
        ...

    @overload
    def __call__(self, subject: str, params: Sequence[Any], /) -> "ScenarioDecorator":
        """
        Enable usage as `@scenario("subject", params)` to set both subject and params.

        :param subject: A custom human-readable subject for the scenario.
        :param params: A sequence of parameter sets for the scenario.
        :return: A new ScenarioDecorator with subject and parameters applied.
        """
        ...

    @overload
    def __call__(self, *, subject: str) -> "ScenarioDecorator":
        """
        Enable usage as `@scenario(subject="subject")` with keyword argument.

        :param subject: A custom human-readable subject for the scenario.
        :return: A new ScenarioDecorator with subject applied.
        """
        ...

    def __call__(self,
                 *args: Any,
                 **kwargs: Any) -> Union[ScenarioDescriptor, "ScenarioDecorator"]:
        raise NotImplementedError()

    def __getitem__(self, item: Any) -> "ScenarioDecorator":
        """
        Apply one or more decorators to the scenario.

        :param item: A decorator or a tuple of decorators to apply.
        :return: A new ScenarioDecorator instance with the specified decorators.
        """
        decorators = item if isinstance(item, tuple) else (item,)
        return ScenarioDecorator(decorators, self._params, self._subject, self._tags)


scenario = ScenarioDecorator()
"""
A flexible decorator for defining Vedro scenarios.
"""
