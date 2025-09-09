from typing import Any, Callable, Optional, Tuple

from vedro._params import CasesType
from vedro._tags import TagsType

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
                 cases: CasesType = (),
                 subject: Optional[str] = None,
                 name: Optional[str] = None,
                 tags: TagsType = ()) -> None:
        """
        Initialize the ScenarioDescriptor with a function, decorators, and parameters.

        :param fn: The function defining the scenario logic.
        :param decorators: A tuple of decorators to apply to the scenario class.
                           Defaults to an empty tuple.
        :param cases: A tuple of parameter sets for parameterized scenarios. Each element
                      should be a callable that provides parameters. Defaults to an empty tuple.
        :param subject: An optional custom human-readable subject for the scenario.
                        If not provided, it will be generated from the function name.
        :param name: Optional generated name for the scenario. If not provided, uses fn.__name__.
        :param tags: Tags to associate with the scenario. Can be a list, tuple, or set
                     of strings or Enums. Defaults to an empty tuple.
        """
        self._fn = fn
        self._decorators = decorators
        self._cases = cases
        self._name = name or fn.__name__
        self._subject = subject
        self._tags = tags

    @property
    def name(self) -> str:
        """
        Get the name of the scenario function.

        :return: The name of the function as a string.
        """
        return self._name

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
    def cases(self) -> CasesType:
        """
        Get the parameterization cases for the scenario.

        :return: A tuple of parameter cases to run the scenario with.
        """
        return self._cases

    @property
    def subject(self) -> Optional[str]:
        """
        Get the custom subject for the scenario.

        :return: The custom subject string or None if not provided.
        """
        return self._subject

    @property
    def tags(self) -> TagsType:
        """
        Get the tags associated with the scenario.

        :return: The tags as a list, tuple, or set of strings or Enums.
        """
        return self._tags
