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
    # 'path' refers to the location of the configuration file.
    # By default, it's set to the location of this file itself (__file__).
    # In practice, this path is dynamically determined at runtime,
    # typically pointing to 'vedro.cfg.py' located in the project directory.
    path: Path = Path(__file__)

    # 'project_dir' is designated as the root directory of the project.
    # It is initially set to the directory from which the application is executed,
    # which is typically the top-level directory of the project.
    # This directory acts as a reference point for rel paths and project-related file operations.
    project_dir: Path = Path.cwd()

    class Registry(Section):
        pass

    class Plugins(Section):
        pass


ConfigType = Type[Config]
