from typing import Any, Callable, Sequence, Tuple, Union, overload

from ._scenario_descriptor import ScenarioDescriptor

__all__ = ("scenario",)


class _ScenarioDecorator:
    def __init__(self, decorators: Tuple[Callable[..., Any], ...] = (),
                 params: Tuple[Any, ...] = ()) -> None:
        self._decorators = decorators
        self._params = params

    @overload
    def __call__(self, /) -> "_ScenarioDecorator":  # pragma: no cover
        ...

    @overload
    def __call__(self, /,
                 fn_or_params: Callable[..., Any]) -> ScenarioDescriptor:  # pragma: no cover
        ...

    @overload
    def __call__(self, /,
                 fn_or_params: Sequence[Any]) -> "_ScenarioDecorator":  # pragma: no cover
        ...

    def __call__(self, /,
                 fn_or_params: Union[Sequence[Any], Callable[..., Any], None] = None
                 ) -> Union[ScenarioDescriptor, "_ScenarioDecorator"]:
        if fn_or_params is None:
            return self

        if callable(fn_or_params):
            return ScenarioDescriptor(fn_or_params, self._decorators, self._params)

        return _ScenarioDecorator(self._decorators, tuple(fn_or_params))

    def __getitem__(self, item: Any) -> "_ScenarioDecorator":
        decorators = item if isinstance(item, tuple) else (item,)
        return _ScenarioDecorator(decorators)


scenario = _ScenarioDecorator()
