import asyncio
from typing import Any

from ._catched import catched
from ._config import Config, computed
from ._context import context
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
from .plugins.skipper import only, skip, skip_if
from .plugins.temp_keeper import create_tmp_dir, create_tmp_file

__version__ = version
__all__ = ("Scenario", "Interface", "run", "only", "skip", "skip_if", "params", "ensure",
           "context", "defer", "defer_global", "Config", "computed", "catched", "create_tmp_dir",
           "create_tmp_file", "attach_artifact", "attach_scenario_artifact",
           "attach_step_artifact", "attach_global_artifact", "MemoryArtifact", "FileArtifact",
           "Artifact",)


def run(*, plugins: Any = None) -> None:
    if plugins is not None:
        raise DeprecationWarning("Argument 'plugins' is deprecated, "
                                 "declare plugins in config (vedro.cfg.py)")

    asyncio.run(main())
