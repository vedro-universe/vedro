from typing import Any, Callable, Optional, Sequence, Tuple, Union, overload

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
    4. With custom subject: `@scenario("subject")` or `@scenario(subject="subject")`
    """

    def __init__(self, decorators: Tuple[Callable[..., Any], ...] = (),
                 params: Tuple[Any, ...] = (),
                 subject: Optional[str] = None) -> None:
        """
        Initialize the scenario decorator with optional decorators, parameters, and subject.

        :param decorators: A tuple of decorators to apply to the scenario class. Defaults to empty.
        :param params: A tuple of parameter sets for scenario parameterization. Defaults to empty.
        :param subject: An optional custom human-readable subject for the scenario.
        """
        self._decorators = decorators
        self._params = params
        self._subject = subject

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

    def __call__(self, *args: Any, **kwargs: Any) -> Union[ScenarioDescriptor, "ScenarioDecorator"]:
        """
        Dispatch the call to either wrap a function, set subject, or set parameterization.

        :return: A ScenarioDescriptor if a function is passed, or a ScenarioDecorator otherwise.
        """
        # Handle keyword-only subject argument
        if "subject" in kwargs:
            subject = kwargs["subject"]
            return ScenarioDecorator(self._decorators, self._params, subject)

        # Handle no arguments: @scenario()
        if len(args) == 0:
            return self

        first_arg = args[0]
        second_arg = args[1] if len(args) > 1 else None

        # Handle function decoration: @scenario directly on function
        if callable(first_arg):
            return ScenarioDescriptor(first_arg, self._decorators, self._params, self._subject)

        # Handle string as subject
        if isinstance(first_arg, str):
            # If second argument is provided, it should be params
            if second_arg is not None:
                return ScenarioDecorator(self._decorators, tuple(second_arg), first_arg)
            # Otherwise, just set the subject
            return ScenarioDecorator(self._decorators, self._params, first_arg)

        # Handle sequence as params (backward compatibility)
        if isinstance(first_arg, (list, tuple)):
            return ScenarioDecorator(self._decorators, tuple(first_arg), self._subject)

        # Default fallback
        return self

    def __getitem__(self, item: Any) -> "ScenarioDecorator":
        """
        Apply one or more decorators to the scenario.

        :param item: A decorator or a tuple of decorators to apply.
        :return: A new ScenarioDecorator instance with the specified decorators.
        """
        decorators = item if isinstance(item, tuple) else (item,)
        return ScenarioDecorator(decorators, self._params, self._subject)


scenario = ScenarioDecorator()
"""
A flexible decorator for defining Vedro scenarios.
"""
