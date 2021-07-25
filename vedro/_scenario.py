from functools import partialmethod
from typing import Any, Dict, Tuple


class _Meta(type):
    def __new__(mcs, name: str, bases: Tuple[Any], namespace: Dict[str, Any]) -> Any:
        if len(bases) == 0:
            return super().__new__(mcs, name, bases, namespace)

        cls_constructor = namespace.get("__init__")
        cls_params = getattr(cls_constructor, "__vedro__params__", None)
        if cls_params is None or len(cls_params) == 0:
            return super().__new__(mcs, name, bases, namespace)

        updated_name = "Template"
        updated_namespace = {**namespace, "__qualname__": updated_name}
        created = super().__new__(mcs, updated_name, bases, updated_namespace)

        cls_globals = getattr(cls_constructor, "__globals__")
        for idx, (args, kwargs) in enumerate(reversed(cls_params), start=1):
            cls_name = f"{name}_{idx}"
            cls_namespace = {
                **namespace,
                "__qualname__": cls_name,
                "__init__": partialmethod(cls_constructor, *args, **kwargs),
                "__vedro__template__": created,
                "__vedro__template_index__": idx,
            }
            cls_globals[cls_name] = type(cls_name, bases, cls_namespace)

        return created


class Scenario(metaclass=_Meta):
    pass
