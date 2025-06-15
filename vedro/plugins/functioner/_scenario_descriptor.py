from typing import Any, Callable, Tuple

__all__ = ("ScenarioDescriptor",)


class ScenarioDescriptor:
    """
    Represents metadata and configuration for a scenario function.

    This descriptor encapsulates the function to be executed as a scenario, along with any
    decorators and parameterizations to be applied. It serves as an intermediary representation
    before scenarios are turned into concrete classes.
    """

    def __init__(self, fn: Callable[..., Any],
                 decorators: Tuple[Callable[..., Any], ...] = (),
                 params: Tuple[Any, ...] = ()) -> None:
        """
        Initialize the ScenarioDescriptor with a function, decorators, and parameters.

        :param fn: The function defining the scenario logic.
        :param decorators: A tuple of decorators to apply to the scenario class.
                           Defaults to an empty tuple.
        :param params: A tuple of parameter sets to use for parameterized scenarios.
                       Defaults to an empty tuple.
        """
        self._fn = fn
        self._decorators = decorators
        self._params = params

    @property
    def name(self) -> str:
        """
        Get the name of the scenario function.

        :return: The name of the function as a string.
        """
        return self._fn.__name__

    @property
    def fn(self) -> Callable[..., Any]:
        """
        Get the scenario function.

        :return: The callable function defining the scenario logic.
        """
        return self._fn

    @property
    def decorators(self) -> Tuple[Callable[..., Any], ...]:
        """
        Get the decorators associated with the scenario.

        :return: A tuple of decorator callables.
        """
        return self._decorators

    @property
    def params(self) -> Tuple[Any, ...]:
        """
        Get the parameter sets associated with the scenario.

        :return: A tuple containing parameter sets for scenario instantiation.
        """
        return self._params
