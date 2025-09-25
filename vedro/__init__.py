import asyncio
from typing import Any, List, Optional

from ._catched import catched
from ._config import Config, computed
from ._context import context
from ._effect import effect
from ._interface import Interface
from ._main import main
from ._params import params
from ._scenario import Scenario
from ._version import version
from .plugins.artifacted import (
    Artifact,
    FileArtifact,
    MemoryArtifact,
    attach_artifact,
    attach_global_artifact,
    attach_scenario_artifact,
    attach_step_artifact,
)
from .plugins.deferrer import defer, defer_global
from .plugins.ensurer import ensure
from .plugins.functioner import given, scenario, then, when
from .plugins.seeder import seed
from .plugins.skipper import only, skip, skip_if
from .plugins.temp_keeper import create_tmp_dir, create_tmp_file

__version__ = version
__all__ = ("Scenario", "Interface", "run", "only", "skip", "skip_if", "params",
           "catched", "scenario", "given", "when", "then", "ensure", "context", "effect",
           "defer", "defer_global", "create_tmp_dir", "create_tmp_file", "attach_artifact",
           "attach_scenario_artifact", "attach_step_artifact", "attach_global_artifact",
           "seed", "Config", "computed", "MemoryArtifact", "FileArtifact", "Artifact",)


def run(argv: Optional[List[str]] = None, *, plugins: Any = None) -> None:
    """
    Run the Vedro test framework with the specified command-line arguments.

    :param argv: Optional list of command-line arguments without the program name.
                 Examples: ["run", "--show-paths"], ["--version"]
    :param plugins: Deprecated. Previously used to pass plugins directly.
                    Now plugins should be declared in the configuration file (vedro.cfg.py).
    """
    if plugins is not None:
        raise DeprecationWarning("Argument 'plugins' is deprecated, "
                                 "declare plugins in config (vedro.cfg.py)")

    asyncio.run(main(argv))
