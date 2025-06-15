from functools import wraps
from typing import TYPE_CHECKING, Any, Callable, Tuple, TypeVar, Union, cast

__all__ = ("params",)

F = TypeVar("F", bound=Callable[..., Any])
ItemType = Union[
    Callable[[F], F],
    Tuple[Callable[[F], F], ...]
]


class Parameterized:
    """
    Represents a parameterized function or method.

    This class is used to store arguments, keyword arguments, and decorators
    for a parameterized test scenario and applies these parameters to the
    specified function when invoked.
    """

    def __init__(self, args: Any, kwargs: Any, decorators: Tuple[Any, ...]) -> None:
        """
        Initialize the Parameterized instance.

        :param args: Positional arguments for the parameterized function.
        :param kwargs: Keyword arguments for the parameterized function.
        :param decorators: A tuple of decorators to be applied to the function.
        """
        self._args = args
        self._kwargs = kwargs
        self._decorators = decorators

    def __call__(self, fn: F) -> F:
        """
        Apply parameters and decorators to the specified function.

        :param fn: The function to which parameters and decorators are applied.
        :return: The updated function with parameters and decorators applied.
        """
        if not hasattr(fn, "__vedro__params__"):
            setattr(fn, "__vedro__params__", [])
        getattr(fn, "__vedro__params__").append((self._args, self._kwargs, self._decorators))
        return fn


class Params:
    """
    Provides a mechanism to define and manage parameterized test scenarios.

    This class is used to create parameterized test cases by storing
    positional and keyword arguments and applying them to a function.
    It also supports applying additional decorators to parameterized functions.
    """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """
        Initialize the Params instance.

        :param args: Positional arguments for the parameterized test.
        :param kwargs: Keyword arguments for the parameterized test.
        """
        self._args = args
        self._kwargs = kwargs

    def __call__(self, fn: F) -> F:
        """
        Apply parameters to the specified function.

        :param fn: The function to which parameters will be applied.
        :return: The updated function with parameters applied.
        """
        return Parameterized(self._args, self._kwargs, ())(fn)

    def __class_getitem__(cls, item: ItemType[F]) -> Callable[..., Parameterized]:
        """
        Create a wrapped parameterized instance with decorators.

        :param item: A single decorator or a tuple of decorators to be applied.
        :return: A callable that creates a Parameterized instance with decorators.
        """
        decorators = item if isinstance(item, tuple) else (item,)

        @wraps(cls)
        def wrapped(*args: Any, **kwargs: Any) -> Parameterized:
            """
            Wrap the parameters with the specified decorators.

            :param args: Positional arguments for the parameterized test.
            :param kwargs: Keyword arguments for the parameterized test.
            :return: A Parameterized instance with the specified parameters and decorators.
            """
            return Parameterized(args, kwargs, decorators)

        return wrapped


if not TYPE_CHECKING:
    params = Params
else:  # pragma: no cover
    # https://github.com/python/mypy/issues/11501
    # So we have to use TYPE_CHECKING here
    _T = TypeVar("_T")

    class TypedParams:
        """
        Provides type-checking support for the `params` decorator.

        This class is a placeholder for `params` during static type checking
        to ensure correct usage and type inference.
        """

        def __call__(self, *args: Any, **kwargs: Any) -> Callable[[_T], _T]:
            """
            Apply parameters to a function during static type checking.

            :param args: Positional arguments for the parameterized test.
            :param kwargs: Keyword arguments for the parameterized test.
            :return: A callable representing the parameterized function.
            """
            return cast(Callable[[_T], _T], ...)

        def __getitem__(self, item: ItemType[F]) -> Callable[..., Callable[[_T], _T]]:
            """
            Create a wrapped parameterized instance with decorators during static type checking.

            :param item: A single decorator or a tuple of decorators to be applied.
            :return: A callable that creates a parameterized function.
            """
            return cast(Callable[..., Callable[[_T], _T]], ...)

    params = TypedParams()
