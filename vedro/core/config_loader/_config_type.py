from pathlib import Path
from typing import Type, Union

import cabina

__all__ = ("Config", "Section", "ConfigType",)


class Section(cabina.Section):
    pass


class Config(cabina.Config, Section):
    # Path to the configuration file. By default, it points to the file
    # where this class is defined (__file__). At runtime, it is typically
    # set to 'vedro.cfg.py' in the project's root directory.
    path: Path = Path(__file__)

    # Root directory of the project, used as a base for resolving relative paths
    # and locating project files. Defaults to the current working directory but
    # can be overridden using the `--project-dir` command-line argument.
    project_dir: Path = Path.cwd()

    # Default location for storing scenario files, located in the "scenarios/"
    # subdirectory of the project's root.
    default_scenarios_dir: Union[Path, str] = "scenarios/"

    class Registry(Section):
        pass

    class Plugins(Section):
        pass


ConfigType = Type[Config]
