from typing import Any, Callable, Optional, Tuple, Union, overload

from vedro._params import CasesType
from vedro._scenario import TagsType

from ._sanitize_identifier import sanitize_identifier
from ._scenario_descriptor import ScenarioDescriptor

__all__ = ("scenario", "ScenarioDecorator",)


class ScenarioDecorator:
    """
    Implements a flexible decorator for defining Vedro scenarios.

    This class allows optional chaining of decorators and parameter sets using
    both decorator syntax and callable invocation.
    """

    def __init__(self, decorators: Tuple[Callable[..., Any], ...] = (),
                 cases: CasesType = (),
                 subject: Optional[str] = None,
                 tags: TagsType = ()) -> None:
        """
        Initialize the scenario decorator with optional decorators, parameters, subject, and tags.

        :param decorators: A tuple of decorators to apply to the scenario class. Defaults to empty.
        :param cases: A tuple of ... Defaults to empty.
        :param subject: An optional custom human-readable subject for the scenario.
        :param tags: Tags to associate with the scenario. Can be a list, tuple, or set
                     of strings or Enums. Defaults to an empty tuple.
        """
        self._decorators = decorators
        self._cases = cases
        self._subject = subject
        self._tags = tags

    @overload
    def __call__(self) -> "ScenarioDecorator":
        ...

    @overload
    def __call__(self, fn: Callable[..., Any], /) -> ScenarioDescriptor:
        ...

    @overload
    def __call__(self, subject: str, cases: CasesType = (), *,
                 tags: TagsType = ()) -> "ScenarioDecorator":
        ...

    @overload
    def __call__(self, cases: CasesType = (), *,
                 subject: str = "",
                 tags: TagsType = ()) -> "ScenarioDecorator":
        ...

    def __call__(self,
                 *args: Any,
                 **kwargs: Any) -> Union[ScenarioDescriptor, "ScenarioDecorator"]:
        if len(args) > 0 and callable(args[0]):
            fn = args[0]
            if len(args) > 1 or len(kwargs) > 0:
                raise TypeError("<message>")
            return self._create_descriptor(fn)

        subject, cases, tags = self._parse_args(args, kwargs)
        return ScenarioDecorator(
            decorators=self._decorators,
            cases=cases,
            subject=subject,
            tags=tags
        )

    def _parse_args(self, args: Any, kwargs: Any) -> Tuple[Union[str, None], CasesType, TagsType]:
        ...
        return None, (), ()

    def _create_descriptor(self, fn: Callable[..., Any]) -> ScenarioDescriptor:
        descriptor = ScenarioDescriptor(
            fn=fn,
            decorators=self._decorators,
            cases=self._cases,
            subject=self._subject,
            tags=self._tags,
        )
        ...
        return descriptor

    def _create_scenario_name(self, subject: str) -> str:
        return sanitize_identifier(subject, prefix="scenario")

    def __getitem__(self, item: Any) -> "ScenarioDecorator":
        """
        Apply one or more decorators to the scenario.

        :param item: A decorator or a tuple of decorators to apply.
        :return: A new ScenarioDecorator instance with the specified decorators.
        """
        decorators = item if isinstance(item, tuple) else (item,)
        return ScenarioDecorator(decorators, self._cases, self._subject, self._tags)


scenario = ScenarioDecorator()
"""
A flexible decorator for defining Vedro scenarios.
"""
