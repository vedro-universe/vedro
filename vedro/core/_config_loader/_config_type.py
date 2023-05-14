from pathlib import Path
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
    # Here, we set __file__ as the fallback value for 'path'
    # However, the actual path will be determined at runtime
    path: Path = Path(__file__)

    class Registry(Section):
        pass

    class Plugins(Section):
        pass


ConfigType = Type[Config]
