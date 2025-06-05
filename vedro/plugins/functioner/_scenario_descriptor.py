from typing import Any, Callable, Tuple

__all__ = ("ScenarioDescriptor",)


class ScenarioDescriptor:
    def __init__(self, fn: Callable[..., Any],
                 decorators: Tuple[Callable[..., Any], ...] = (),
                 params: Tuple[Any, ...] = ()) -> None:
        self._fn = fn
        self._decorators = decorators
        self._params = params

    @property
    def name(self) -> str:
        return self._fn.__name__

    @property
    def fn(self) -> Callable[..., Any]:
        return self._fn

    @property
    def decorators(self) -> Tuple[Callable[..., Any], ...]:
        return self._decorators

    @property
    def params(self) -> Tuple[Any, ...]:
        return self._params
