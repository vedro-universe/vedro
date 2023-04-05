import inspect
from functools import partialmethod
from typing import Any, Dict, Tuple


class _Meta(type):
    def __new__(mcs, name: str, bases: Tuple[Any], namespace: Dict[str, Any]) -> Any:
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
        for idx, (args, kwargs) in enumerate(reversed(cls_params), start=1):
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
            cls_globals[cls_name] = type(cls_name, bases, cls_namespace)

        return created


class Scenario(metaclass=_Meta):
    subject: str

    def __repr__(self) -> str:
        return "<Scenario>"
