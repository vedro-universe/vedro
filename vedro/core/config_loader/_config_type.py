from pathlib import Path
from typing import Type, Union

import cabina

__all__ = ("Config", "Section", "ConfigType", "computed", "env", "lazy_env",)


class Section(cabina.Section):
    """
    Represents a base configuration section.

    This class extends `cabina.Section` and is used as a foundation for grouping
    related configuration options. Framework-specific configurations can subclass
    `Section` to define custom sections.
    """
    pass


class Config(cabina.Config, Section):
    """
    Base configuration class for applications.

    The `Config` class provides the foundation for managing configuration options,
    such as paths, directories, and custom settings. It is designed to be extended by other
    configurations for more specialized use cases.

    This class is built on top of `cabina.Config` and `Section`, inheriting
    their capabilities while offering core options such as the project root,
    configuration file paths, and default directories.
    """

    path: Path = Path(__file__)
    """
    Path to the configuration file.

    By default, this points to the file where the `Config` class is defined
    (`__file__`). At runtime, this is typically set to `'vedro.cfg.py'` in
    the project's root directory.
    """

    project_dir: Path = Path.cwd()
    """
    Root directory of the project.

    This is used as a base for resolving relative paths and locating project
    files. By default, it is set to the current working directory (`cwd`), but
    it can be overridden using the `--project-dir` command-line argument.
    """

    default_scenarios_dir: Union[Path, str] = "scenarios/"
    """
    Default location for storing scenario files.

    This defaults to the `"scenarios/"` subdirectory of the project's root directory.
    It can be set as a `Path` or a `str` and is used for discovering scenario files.
    """

    class Registry(Section):
        """
        Base section for registry-related configuration.

        Subclasses of `Config` can extend this section to include runtime
        registry options, such as factories or dependency injection configurations.
        """
        pass

    class Plugins(Section):
        """
        Base section for plugins-related configuration.

        Framework-specific configurations can extend this section to manage
        plugin settings (e.g., enabling/disabling plugins, setting plugin options).
        """
        pass


ConfigType = Type[Config]
"""
Alias for the type of the `Config` class.

This can be used for type annotations or runtime type checking.
"""

computed = cabina.computed
"""
Decorator for computed configuration properties.

This is a re-export of `cabina.computed`, allowing you to define dynamic
configuration options whose values are computed based on other properties.
"""

env = cabina.env
"""
Decorator to define environment-variable-based configuration properties.

This is a re-export of `cabina.env`, used to declare configuration properties
whose values are populated from environment variables.
"""

lazy_env = getattr(cabina, "lazy_env", env)  # backward compatibility for older versions
"""
Decorator to define lazily evaluated environment-variable-based properties.

This is a re-export of `cabina.lazy_env`, allowing you to lazily resolve
configuration values from environment variables upon first access.
"""
