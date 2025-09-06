from typing import Any, Callable, Dict, Optional, Sequence, Tuple, Union, overload

from vedro._scenario import TagsType

from ._errors import DuplicateScenarioError
from ._scenario_descriptor import ScenarioDescriptor

__all__ = ("scenario", "ScenarioDecorator",)


class ScenarioDecorator:
    """
    Implements a flexible decorator for defining Vedro scenarios.

    This class allows optional chaining of decorators and parameter sets using
    both decorator syntax and callable invocation.
    """

    def __init__(self, decorators: Tuple[Callable[..., Any], ...] = (),
                 params: Tuple[Any, ...] = (),
                 subject: Optional[str] = None,
                 tags: TagsType = ()) -> None:
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
        """
        Handle various decorator invocation patterns.

        This method supports multiple calling conventions:
        - Direct decoration: @scenario
        - Empty call: @scenario()
        - With subject: @scenario("subject") or @scenario(subject="subject")
        - With params: @scenario([params]) or @scenario(cases=[params])
        - With tags: @scenario(tags={tags})
        - Combined: @scenario("subject", [params], tags={tags})

        :param args: Positional arguments (function, subject, params)
        :param kwargs: Keyword arguments (subject, cases/params, tags)
        :return: ScenarioDescriptor if decorating a function, ScenarioDecorator for chaining
        """
        # Step 1: Normalize arguments by converting kwargs to positional args
        normalized_args = self._normalize_args(args, kwargs)

        # Step 2: Determine what to return
        if self._should_return_decorator(normalized_args):
            return self._create_decorator(normalized_args)
        else:
            return self._create_descriptor(normalized_args)

    def _normalize_args(self, args: Tuple[Any, ...], kwargs: Dict[str, Any]) -> Tuple[Any, ...]:
        """
        Normalize keyword arguments into positional arguments.

        :param args: Original positional arguments
        :param kwargs: Keyword arguments to normalize
        :return: Normalized tuple of arguments
        """
        result = list(args)

        # Extract subject from kwargs
        if "subject" in kwargs:
            # Insert subject at the beginning if no string is already there
            subject = kwargs["subject"]
            if not result or not isinstance(result[0], str):
                result.insert(0, subject)

        # Extract params/cases from kwargs (cases is an alias for params)
        if "cases" in kwargs:
            params = kwargs["cases"]
            # Add params after subject (if present) but before any function
            insert_pos = 0
            if result and isinstance(result[0], str):
                insert_pos = 1
            if insert_pos < len(result) and not callable(result[insert_pos]):
                result.insert(insert_pos, params)
            else:
                result.append(params)

        # Extract tags from kwargs
        if "tags" in kwargs:
            tags = kwargs["tags"]
            # Add tags at the end
            result.append(tags)

        return tuple(result)

    def _should_return_decorator(self, args: Tuple[Any, ...]) -> bool:
        """
        Determine if we should return a ScenarioDecorator for chaining.

        :param args: Normalized arguments
        :return: True if should return decorator, False if should return descriptor
        """
        # Empty call or no callable in args means we return a decorator
        if not args:
            return True

        # If first arg is callable, we're decorating a function directly
        if callable(args[0]):
            return False

        # If we have non-callable args (subject, params, tags), return decorator
        return True

    def _parse_args(self, args: Tuple[Any, ...]
                    ) -> Tuple[Optional[str], Tuple[Any, ...], TagsType]:
        """
        Parse arguments to extract subject, params, and tags.

        :param args: Arguments to parse
        :return: Tuple of (subject, params, tags)
        """
        subject = self._subject
        params = self._params
        tags = self._tags

        for arg in args:
            if isinstance(arg, str):
                # First string is subject
                if subject is None:
                    subject = arg
            elif isinstance(arg, (list, tuple)):
                # Sequence is params/cases
                params = tuple(arg)
            elif isinstance(arg, (set, frozenset)):
                # Set is tags
                tags = arg
            elif callable(arg):
                # Skip callables in parsing
                continue

        return subject, params, tags

    def _create_decorator(self, args: Tuple[Any, ...]) -> "ScenarioDecorator":
        """
        Create a new ScenarioDecorator with updated properties.

        :param args: Arguments to parse for decorator properties
        :return: New ScenarioDecorator instance
        """
        subject, params, tags = self._parse_args(args)
        return ScenarioDecorator(self._decorators, params, subject, tags)

    def _create_descriptor(self, args: Tuple[Any, ...]) -> ScenarioDescriptor:
        """
        Create the final ScenarioDescriptor.

        :param args: Arguments with the function as first element
        :return: ScenarioDescriptor instance
        """
        # First arg must be the function
        fn = args[0]

        # Parse remaining args for properties
        subject, params, tags = self._parse_args(args[1:])

        # Check for anonymous function without subject
        if fn.__name__ == "_" and not subject:
            raise DuplicateScenarioError(
                "Anonymous scenario function '_' requires a subject. "
                "Use @scenario('subject') to provide one."
            )

        # Generate scenario name from subject if provided, otherwise use function name
        if subject:
            scenario_name = self._generate_scenario_name(subject)
        else:
            scenario_name = fn.__name__

        # Check for duplicates in globals
        if scenario_name in fn.__globals__:
            existing = fn.__globals__[scenario_name]
            # Check if it's a scenario descriptor (not some other global)
            if isinstance(existing, ScenarioDescriptor):
                if fn.__name__ == "_":
                    # Duplicate subject for anonymous functions
                    raise DuplicateScenarioError(
                        f"Duplicate scenario with subject '{subject}' found. "
                        f"Each anonymous scenario must have a unique subject."
                    )
                else:
                    # Duplicate function name
                    raise DuplicateScenarioError(
                        f"Duplicate scenario function '{scenario_name}' found. "
                        f"Each scenario function must have a unique name."
                    )

        # Create the descriptor with the generated name
        descriptor = ScenarioDescriptor(fn, self._decorators, params, subject, scenario_name, tags)
        
        # Store descriptor in globals for anonymous functions
        if fn.__name__ == "_":
            # For anonymous functions, store with generated name
            fn.__globals__[scenario_name] = descriptor
        
        return descriptor

    def _generate_scenario_name(self, subject: Optional[str]) -> str:
        """
        Generate a valid Python identifier from subject.

        :param subject: The subject string to convert
        :return: A valid Python identifier
        """
        if subject:
            # Convert "create user" -> "create_user"
            # Remove invalid characters and ensure it's a valid Python identifier
            import re

            # Replace spaces and hyphens with underscores
            name = re.sub(r'[\s\-]+', '_', subject)
            # Remove non-alphanumeric characters (except underscores)
            name = re.sub(r'[^\w]', '', name)
            # Ensure it doesn't start with a digit
            if name and name[0].isdigit():
                name = f"scenario_{name}"
            return name.lower() if name else f"scenario_{id(self)}"
        else:
            # Generate unique name if no subject
            return f"scenario_{id(self)}"

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
