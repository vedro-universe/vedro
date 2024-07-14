from pathlib import Path
from typing import Type

import cabina

__all__ = ("Config", "Section", "ConfigType",)


class Section(cabina.Section):
    pass


class Config(cabina.Config, Section):
    # 'path' refers to the location of the configuration file.
    # By default, it's set to the location of this file itself (__file__).
    # In practice, this path is dynamically determined at runtime,
    # typically pointing to 'vedro.cfg.py' located in the project directory.
    path: Path = Path(__file__)

    # The `project_dir` property is designated as the root directory of the project,
    # serving as a reference point for relative paths and project-related file operations.
    # Although it defaults to the directory from which the application is executed,
    # this setting can be overridden via the `--project-dir` argument.
    project_dir: Path = Path.cwd()

    class Registry(Section):
        pass

    class Plugins(Section):
        pass


ConfigType = Type[Config]
