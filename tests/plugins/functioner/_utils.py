import os
from pathlib import Path

import pytest

from vedro.core import ModuleFileLoader, ModuleLoader
from vedro.core.scenario_collector import ScenarioSource
from vedro.plugins.functioner._scenario_provider import ScenarioProvider

__all__ = ("tmp_dir", "provider", "module_loader", "scenario_source",)


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
def module_loader() -> ModuleLoader:
    return ModuleFileLoader()


@pytest.fixture()
def provider() -> ScenarioProvider:
    return ScenarioProvider()


@pytest.fixture()
def scenario_source(tmp_dir: Path, module_loader: ModuleLoader) -> ScenarioSource:
    project_dir = tmp_dir
    path = project_dir / "scenarios" / "scenario.py"
    return ScenarioSource(path, project_dir, module_loader)
