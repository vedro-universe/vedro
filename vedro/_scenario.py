import inspect
from functools import partialmethod
from typing import Any, Dict, Tuple

from .core._meta_data import MetaData

__all__ = ("Scenario",)


class _Meta(type):
    # In v2, this logic should be moved to a `ScenarioLoader` to better encapsulate and
    # separate the behavior, making it easier to maintain and extend.
    # However, making this change now would break backward compatibility for external plugins
    # that rely on the current metaclass design.

    def __new__(mcs, name: str, bases: Tuple[Any], namespace: Dict[str, Any]) -> Any:
        namespace["__vedro__meta__"] = MetaData()

        if len(bases) == 0:
            return super().__new__(mcs, name, bases, namespace)

        for base in bases:
            if base != Scenario:
                module = namespace.get("__module__", "")
                raise TypeError(f"Subclassing is restricted <{module}.{name}>")

        cls_constructor = namespace.get("__init__")
        cls_params = getattr(cls_constructor, "__vedro__params__", None)
        if cls_params is None or len(cls_params) == 0:
            return super().__new__(mcs, name, bases, namespace)

        updated_name = "VedroTemplate"
        updated_namespace = {**namespace, "__qualname__": updated_name}
        created = super().__new__(mcs, updated_name, bases, updated_namespace)

        cls_globals = getattr(cls_constructor, "__globals__")
        for idx, (args, kwargs, decorators) in enumerate(reversed(cls_params), start=1):
            signature = inspect.signature(cls_constructor)  # type: ignore

            try:
                bound_args = signature.bind(None, *args, **kwargs)
            except BaseException as e:
                module = namespace.get("__module__", "")
                raise TypeError(f"{e} <{module}.{name}>") from None

            bound_args.apply_defaults()

            cls_name = f"{name}_{idx}_VedroScenario"
            cls_namespace = {
                **namespace,
                "__qualname__": cls_name,
                "__init__": partialmethod(cls_constructor, *args, **kwargs),
                "__vedro__template_name__": name,
                "__vedro__template__": created,
                "__vedro__template_index__": idx,
                "__vedro__template_total__": len(cls_params),
                "__vedro__template_args__": bound_args,
            }
            cls = type(cls_name, bases, cls_namespace)
            for decorator in decorators:
                cls = decorator(cls)
            cls_globals[cls_name] = cls

        return created


class Scenario(metaclass=_Meta):
    subject: str

    def __repr__(self) -> str:
        return "<Scenario>"
