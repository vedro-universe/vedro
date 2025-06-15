from typing import Any, Callable, Sequence, Tuple, Union, overload

from ._scenario_descriptor import ScenarioDescriptor

__all__ = ("scenario", "ScenarioDecorator",)


class ScenarioDecorator:
    """
    Implements a flexible decorator for defining Vedro scenarios.

    This class allows optional chaining of decorators and parameter sets using
    both decorator syntax and callable invocation. It supports three primary usages:

    1. As a plain decorator: `@scenario`
    2. With parameters: `@scenario(params)`
    3. With additional class decorators: `@scenario[decorator]`
    """

    def __init__(self, decorators: Tuple[Callable[..., Any], ...] = (),
                 params: Tuple[Any, ...] = ()) -> None:
        """
        Initialize the scenario decorator with optional decorators and parameters.

        :param decorators: A tuple of decorators to apply to the scenario class. Defaults to empty.
        :param params: A tuple of parameter sets for scenario parameterization. Defaults to empty.
        """
        self._decorators = decorators
        self._params = params

    @overload
    def __call__(self, /) -> "ScenarioDecorator":
        """
        Enable usage as `@scenario()`.

        :return: The scenario decorator instance itself for chaining.
        """
        ...

    @overload
    def __call__(self, /,
                 fn_or_params: Callable[..., Any]) -> ScenarioDescriptor:
        """
        Enable usage as `@scenario` directly on a function.

        :param fn_or_params: The function to decorate as a scenario.
        :return: A ScenarioDescriptor representing the scenario.
        """
        ...

    @overload
    def __call__(self, /,
                 fn_or_params: Sequence[Any]) -> "ScenarioDecorator":
        """
        Enable usage as `@scenario(params)` to set parameterization.

        :param fn_or_params: A sequence of parameter sets for the scenario.
        :return: A new ScenarioDecorator with parameters applied.
        """
        ...

    def __call__(self, /,
                 fn_or_params: Union[Sequence[Any], Callable[..., Any], None] = None
                 ) -> Union[ScenarioDescriptor, "ScenarioDecorator"]:
        """
        Dispatch the call to either wrap a function or set parameterization.

        :param fn_or_params: Can be a callable function, a sequence of parameters, or None.
        :return: A ScenarioDescriptor if a function is passed, or a ScenarioDecorator otherwise.
        """
        if fn_or_params is None:
            return self

        if callable(fn_or_params):
            return ScenarioDescriptor(fn_or_params, self._decorators, self._params)

        return ScenarioDecorator(self._decorators, tuple(fn_or_params))

    def __getitem__(self, item: Any) -> "ScenarioDecorator":
        """
        Apply one or more decorators to the scenario.

        :param item: A decorator or a tuple of decorators to apply.
        :return: A new ScenarioDecorator instance with the specified decorators.
        """
        decorators = item if isinstance(item, tuple) else (item,)
        return ScenarioDecorator(decorators)


scenario = ScenarioDecorator()
"""
A flexible decorator for defining Vedro scenarios.
"""
