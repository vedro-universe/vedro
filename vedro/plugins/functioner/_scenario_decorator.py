from typing import Any, Callable, Optional, Tuple, Union, overload

from vedro._params import CasesType
from vedro._scenario import TagsType

from ._errors import DuplicateScenarioError
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
        # If first argument is a callable, it's a direct decoration
        if len(args) > 0 and callable(args[0]):
            fn = args[0]
            # Don't allow additional arguments when decorating a function directly
            if len(args) > 1 or len(kwargs) > 0:
                raise TypeError(
                    f"scenario() takes 1 positional argument when decorating a function "
                    f"but {len(args)} were given with {len(kwargs)} keyword arguments"
                )
            return self._create_descriptor(fn)

        # Otherwise, parse arguments to create a new decorator
        subject, cases, tags = self._parse_args(args, kwargs)
        return ScenarioDecorator(
            decorators=self._decorators,
            cases=cases,
            subject=subject,
            tags=tags
        )

    def _parse_args(self, args: Any, kwargs: Any) -> Tuple[Union[str, None], CasesType, TagsType]:
        """
        Parse arguments to extract subject, cases, and tags.

        :param args: Positional arguments passed to the decorator
        :param kwargs: Keyword arguments passed to the decorator
        :return: A tuple of (subject, cases, tags)
        """
        subject = self._subject
        cases = self._cases
        tags = self._tags

        # Track what was set from positional arguments
        subject_from_args = False
        cases_from_args = False

        # Handle positional arguments
        if len(args) == 0:
            # No positional args, check kwargs
            pass
        elif len(args) == 1:
            # Single positional arg could be subject (str) or cases (list/tuple)
            if isinstance(args[0], str):
                subject = args[0]
                subject_from_args = True
            elif isinstance(args[0], (list, tuple)):
                cases = args[0]
                cases_from_args = True
            else:
                raise TypeError(
                    f"First positional argument must be either str (subject) or "
                    f"list/tuple (cases), got {type(args[0]).__name__}"
                )
        elif len(args) == 2:
            # Two positional args: subject and cases
            if not isinstance(args[0], str):
                raise TypeError(
                    f"When providing two positional arguments, first must be str (subject), "
                    f"got {type(args[0]).__name__}"
                )
            if not isinstance(args[1], (list, tuple)):
                raise TypeError(
                    f"When providing two positional arguments, second must be list or "
                    f"tuple (cases), got {type(args[1]).__name__}"
                )
            subject = args[0]
            cases = args[1]
            subject_from_args = True
            cases_from_args = True
        else:
            raise TypeError(
                f"scenario() takes at most 2 positional arguments ({len(args)} given)"
            )

        # Handle keyword arguments
        if 'subject' in kwargs:
            if subject_from_args:
                raise TypeError("Got multiple values for argument 'subject'")
            subject = kwargs['subject']
            if subject is not None and not isinstance(subject, str):
                raise TypeError(
                    f"subject must be str or None, got {type(subject).__name__}"
                )

        if 'cases' in kwargs:
            if cases_from_args:
                raise TypeError("Got multiple values for argument 'cases'")
            cases = kwargs['cases']
            # CasesType is list or tuple
            if not isinstance(cases, (list, tuple)):
                raise TypeError(
                    f"cases must be list or tuple, got {type(cases).__name__}"
                )

        if 'tags' in kwargs:
            tags = kwargs['tags']
            # TagsType is list, tuple, or set
            if not isinstance(tags, (list, tuple, set)):
                raise TypeError(
                    f"tags must be list, tuple, or set, got {type(tags).__name__}"
                )

        # Check for unexpected keyword arguments
        allowed_kwargs = {'subject', 'cases', 'tags'}
        unexpected = set(kwargs.keys()) - allowed_kwargs
        if unexpected:
            raise TypeError(
                f"scenario() got unexpected keyword argument(s): {', '.join(sorted(unexpected))}"
            )

        return subject, cases, tags

    def _create_descriptor(self, fn: Callable[..., Any]) -> ScenarioDescriptor:
        """
        Create a ScenarioDescriptor from a function.

        :param fn: The function to create a descriptor for
        :return: A ScenarioDescriptor instance
        """
        if fn.__name__ == "_" and not self._subject:
            raise DuplicateScenarioError(
                "Anonymous scenario function '_' requires a subject. "
                "Use @scenario('subject') to provide one."
            )

        if self._subject:
            descriptor_name = self._create_scenario_name(self._subject)
        else:
            descriptor_name = fn.__name__

        descriptor = ScenarioDescriptor(
            fn=fn,
            decorators=self._decorators,
            cases=self._cases,
            subject=self._subject,
            name=descriptor_name,
            tags=self._tags,
        )

        existing = fn.__globals__.get(descriptor_name)
        if (existing is not None) and isinstance(existing, ScenarioDescriptor):
            if self._subject:
                raise DuplicateScenarioError(
                    f"Duplicate scenario with subject '{self._subject}' found. "
                    "Each anonymous scenario must have a unique subject."
                )
            else:
                raise DuplicateScenarioError(
                    f"Duplicate scenario function '{descriptor_name}' found. "
                    "Each scenario function must have a unique name."
                )

        if fn.__name__ == "_" and self._subject:
            fn.__globals__[descriptor_name] = descriptor

        return descriptor

    def _create_scenario_name(self, subject: str) -> str:
        """
        Create a valid Python identifier from a subject string.

        :param subject: The human-readable subject string
        :return: A valid Python identifier
        """
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
