from typing import Any, Type

import cabina
from cabina import MetaBase
from cabina.errors import ConfigError

__all__ = ("Config", "Section", "ConfigType",)


class _MetaBase(MetaBase):
    def __call__(cls, *args: Any, **kwargs: Any) -> None:
        try:
            super().__call__(*args, **kwargs)
        except ConfigError:
            # backward compatibility
            raise DeprecationWarning("Declare plugin in config (vedro.cfg.py)")


class Section(cabina.Section, metaclass=_MetaBase):
    pass


class Config(cabina.Config, Section):
    class Registry(Section):
        pass

    class Plugins(Section):
        pass


ConfigType = Type[Config]
