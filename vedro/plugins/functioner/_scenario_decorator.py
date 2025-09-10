import inspect
import os
from inspect import iscoroutinefunction, isfunction
from typing import Any, Callable, Optional, Tuple, Union, overload

from vedro._params import CasesType
from vedro._tags import TagsType

from ._errors import DuplicateScenarioError, FunctionShadowingError
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
        :param cases: A tuple of parameter sets for parameterized scenarios. Each element
                      should be a callable that provides parameters. Defaults to empty.
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

    # TODO: Remove this overload in v2 to simplify arg parsing (kept for backward compatibility)
    @overload
    def __call__(self, cases: CasesType = (), *,
                 subject: str = "",
                 tags: TagsType = ()) -> "ScenarioDecorator":
        ...

    def __call__(self,
                 *args: Any,
                 **kwargs: Any) -> Union[ScenarioDescriptor, "ScenarioDecorator"]:
        """
        Make the decorator callable, supporting multiple usage patterns.

        This method enables flexible usage of the @scenario decorator:
        - @scenario - Direct decoration without arguments
        - @scenario(fn) - Direct decoration of a function
        - @scenario(subject) - Decoration with a custom subject string
        - @scenario(cases) - Decoration with parameter cases (backward compatibility)
        - @scenario(subject, cases) - Decoration with both subject and cases
        - @scenario(subject=..., cases=..., tags=...) - Keyword arguments

        :param args: Variable positional arguments
        :param kwargs: Variable keyword arguments
        :return: Either a ScenarioDescriptor (when decorating a function directly)
                 or a new ScenarioDecorator instance (when configuring parameters)
        :raises TypeError: If arguments don't match any valid pattern
        """
        # If first argument is a callable, it's a direct decoration
        if len(args) > 0 and callable(args[0]):
            fn = args[0]
            # Don't allow additional arguments when decorating a function directly
            if len(args) > 1 or len(kwargs) > 0:
                raise TypeError(
                    f"@scenario() takes 1 positional argument when decorating a function "
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
        subject: Union[str, None] = None
        cases: CasesType = ()
        tags: TagsType = ()

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
                subject = args[0].strip()
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
            subject = args[0].strip()
            cases = args[1]
            subject_from_args = True
            cases_from_args = True
        else:
            raise TypeError(
                f"@scenario() takes at most 2 positional arguments ({len(args)} given)"
            )

        # Handle keyword arguments
        if 'subject' in kwargs:
            if subject_from_args:
                raise TypeError("Got multiple values for argument 'subject'")
            subject = kwargs['subject']
            if (subject is None) or (not isinstance(subject, str)):
                raise TypeError(
                    f"subject must be str, got {type(subject).__name__}"
                )
            subject = subject.strip()

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
                f"@scenario() got unexpected keyword argument(s): {', '.join(sorted(unexpected))}"
            )

        return subject, cases, tags

    def _create_descriptor(self, fn: Callable[..., Any]) -> ScenarioDescriptor:
        """
        Create a ScenarioDescriptor from a function.

        :param fn: The function to convert into a scenario descriptor.
        :return: A ScenarioDescriptor instance.
        :raises TypeError: If fn is not a regular function or async function.
        :raises DuplicateScenarioError: If an anonymous function is used without a subject or
                                        naming conflicts exist.
        :raises FunctionShadowingError: If the scenario would shadow an existing non-scenario
                                        function.
        """
        if not (isfunction(fn) or iscoroutinefunction(fn)):
            location = self._get_location_info(fn)
            if hasattr(fn, "__name__"):
                name = f"'{fn.__name__}' ({type(fn).__name__})"
            else:
                name = f"{type(fn).__name__}"
            raise TypeError(
                f"@scenario decorator cannot be used on {name} {location}. "
                f"It can only decorate regular functions defined with 'def' or 'async def'."
            )

        if not hasattr(fn, "__globals__"):  # pragma: no cover
            location = self._get_location_info(fn)
            if hasattr(fn, "__name__"):
                name = f"'{fn.__name__}' ({type(fn).__name__})"
            else:
                name = f"{type(fn).__name__}"
            raise TypeError(
                f"@scenario decorator cannot be used on {name} {location}. "
                f"It can only decorate regular functions defined with 'def' or 'async def'."
            )

        if self._is_anonymous_function(fn) and not self._subject:
            location = self._get_location_info(fn)
            raise DuplicateScenarioError(
                f"Scenario function '_' {location} needs a subject. "
                "Add one like this: @scenario('your subject here')"
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

        existing_obj = fn.__globals__.get(descriptor_name)
        if existing_obj is not None:
            self._validate_no_conflict(existing_obj, descriptor)

        if self._is_anonymous_function(fn) and self._subject:
            # This is a temporary and dirty workaround; to be revisited after the v2 release
            fn.__globals__[descriptor_name] = descriptor

        return descriptor

    def _validate_no_conflict(self, existing_obj: Union[ScenarioDescriptor, Any],
                              descriptor: ScenarioDescriptor) -> None:
        """
        Validate that creating a scenario with the given name won't conflict
        with existing definitions.

        :param existing_obj: The existing object in the namespace
        :param descriptor: The ScenarioDescriptor being created
        :raises DuplicateScenarioError: If a scenario with this name already exists
        :raises FunctionShadowingError: If this would shadow a non-scenario function
        """
        # Check for duplicate ScenarioDescriptor
        if isinstance(existing_obj, ScenarioDescriptor):
            if self._subject:
                location = self._get_location_info(descriptor.fn)
                raise DuplicateScenarioError(
                    f"Multiple scenarios found with subject '{self._subject}' {location}. "
                    "When using anonymous functions (like '_'), each must have a unique subject. "
                    "Consider renaming one or using named functions instead."
                )
            else:
                location = self._get_location_info(descriptor.fn)
                raise DuplicateScenarioError(
                    f"Found duplicate scenario '{descriptor.name}' {location}. "
                    "Please rename one of the scenarios to have a unique name."
                )

        # Check for function shadowing: when a non-ScenarioDescriptor exists with the same name
        else:
            if self._is_anonymous_function(descriptor.fn) and self._subject:
                location = self._get_location_info(descriptor.fn)
                raise FunctionShadowingError(
                    f"Subject '{self._subject}' {location} would create a conflict with existing "
                    f"function '{descriptor.name}'. Please either: "
                    "1) Choose a different subject, or "
                    "2) Rename the existing function"
                )
            elif not self._is_anonymous_function(descriptor.fn):
                location = self._get_location_info(descriptor.fn)
                raise FunctionShadowingError(
                    f"Scenario '{descriptor.name}' {location} conflicts with an existing "
                    "function. Please either: "
                    "1) Rename your scenario function, or "
                    "2) Rename the existing function"
                )

    def _get_location_info(self, fn: Callable[..., Any]) -> str:
        """
        Get human-readable location information for a function.

        WARNING: This method is SLOW and should ONLY be used for error messages.
        It performs expensive operations like file I/O and source code inspection.
        Never use this in hot paths or normal execution flow.

        Attempts to retrieve location information in the following priority:
        1. File path with line number (best case): "at 'path/to/file.py:123'"
        2. Module name (fallback): "in module 'module.name'"
        3. Unknown location (worst case): "(location unknown)"

        :param fn: The function to get location information for
        :return: A string describing the function's location, formatted for use in error messages
        """
        try:
            source_file = inspect.getsourcefile(fn)
            source_lines = inspect.getsourcelines(fn)
        except:  # noqa: E722
            source_file = source_lines = None

        if source_file and source_lines:
            try:
                rel_path = os.path.relpath(source_file)
            except ValueError:
                rel_path = source_file
            _, lineno = source_lines
            return f"at '{rel_path}:{lineno}'"

        module = inspect.getmodule(fn)
        if module:
            return f"in module '{module.__name__}'"

        return "(location unknown)"

    def _is_anonymous_function(self, fn: Callable[..., Any]) -> bool:
        """
        Check if a function is an anonymous function (named '_').

        :param fn: The function to check.
        :return: True if the function is anonymous, False otherwise.
        """
        try:
            return fn.__name__ == "_"
        except AttributeError:
            return True

    # (!) Do not rely on this function's behavior, it may change even in a minor version
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
