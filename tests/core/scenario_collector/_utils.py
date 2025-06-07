import os
from pathlib import Path
from types import ModuleType
from unittest.mock import AsyncMock, Mock

import pytest

from vedro.core import ModuleLoader

__all__ = ("tmp_dir", "loaded_module", "module_loader",)


@pytest.fixture()
def tmp_dir(tmp_path: Path) -> Path:
    cwd = os.getcwd()
    try:
        os.chdir(tmp_path)

        Path("./scenarios").mkdir(exist_ok=True)
        yield tmp_path
    finally:
        os.chdir(cwd)


@pytest.fixture()
def loaded_module() -> ModuleType:
    return Mock(ModuleType)


@pytest.fixture()
def module_loader(loaded_module: ModuleType) -> ModuleLoader:
    return Mock(ModuleLoader, load=AsyncMock(return_value=loaded_module))
