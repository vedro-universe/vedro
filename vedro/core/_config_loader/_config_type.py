from typing import Type

import cabina

__all__ = ("Config", "Section", "ConfigType",)


class Section(cabina.Section):
    pass


class Config(cabina.Config, cabina.Section):
    class Plugins(Section):
        pass


ConfigType = Type[Config]
