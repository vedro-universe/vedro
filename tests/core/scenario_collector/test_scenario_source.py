from pathlib import Path
from textwrap import dedent
from types import ModuleType
from unittest.mock import AsyncMock, Mock, call

import pytest
from baby_steps import given, then, when

from vedro.core import ModuleLoader
from vedro.core.scenario_collector import ScenarioSource

from ._utils import tmp_dir

__all__ = ("tmp_dir",)  # fixtures


@pytest.fixture()
def loaded_module() -> ModuleType:
    return Mock(ModuleType)


@pytest.fixture()
def module_loader(loaded_module: ModuleType) -> ModuleLoader:
    return Mock(ModuleLoader, load=AsyncMock(return_value=loaded_module))


async def test_properties_of_scenario_source(tmp_dir: Path, module_loader: ModuleLoader):
    with given:
        project_dir = tmp_dir
        path = project_dir / "scenarios" / "scenario.py"

    with when:
        source = ScenarioSource(path, project_dir, module_loader)

    with then:
        assert source.path == path
        assert source.project_dir == project_dir
        assert source.rel_path == Path("scenarios/scenario.py")


async def test_get_module_first_time(tmp_dir: Path, module_loader: ModuleLoader,
                                     loaded_module: ModuleType,):
    with given:
        project_dir = tmp_dir
        path = project_dir / "scenarios" / "scenario.py"
        source = ScenarioSource(path, project_dir, module_loader)

    with when:
        module = await source.get_module()

    with then:
        assert module is loaded_module
        assert module_loader.mock_calls == [call.load(path)]


async def test_get_module_uses_cache(tmp_dir: Path, module_loader: ModuleLoader,
                                     loaded_module: ModuleType,):
    with given:
        project_dir = tmp_dir
        path = project_dir / "scenarios" / "scenario.py"
        source = ScenarioSource(path, project_dir, module_loader)
        await source.get_module()  # Preload module

    with when:
        module = await source.get_module()  # Should use cached module

    with then:
        assert module is loaded_module
        assert module_loader.mock_calls == [call.load(path)]


async def test_get_content_first_time(tmp_dir: Path, module_loader: ModuleLoader):
    with given:
        project_dir = tmp_dir
        path = project_dir / "scenarios" / "scenario.py"
        path.write_text(scenario_content := dedent("""
            import vedro
            class TestScenario(vedro.Scenario):
                pass
        """))

        scenario_path = Mock(wraps=Path(path))
        source = ScenarioSource(scenario_path, project_dir, module_loader)

    with when:
        content = await source.get_content()

    with then:
        assert content == scenario_content
        assert scenario_path.mock_calls == [
            call.is_absolute(),
            call.read_text()
        ]


async def test_get_content_uses_cache(tmp_dir: Path, module_loader: ModuleLoader):
    with given:
        project_dir = tmp_dir
        path = project_dir / "scenarios" / "scenario.py"
        path.write_text(scenario_content := dedent("""
            import vedro
            class TestScenario(vedro.Scenario):
                pass
        """))

        scenario_path = Mock(wraps=Path(path))
        source = ScenarioSource(scenario_path, project_dir, module_loader)
        await source.get_content()  # Preload content

    with when:
        content = await source.get_content()  # Should use cached content

    with then:
        assert content == scenario_content
        assert scenario_path.mock_calls == [
            call.is_absolute(),
            call.read_text()
        ]
