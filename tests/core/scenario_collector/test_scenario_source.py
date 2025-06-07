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
        assert module_loader.mock_calls == [call.load(source.rel_path)]


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
        assert module_loader.mock_calls == [call.load(source.rel_path)]


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


def test_equal_sources_with_same_path_are_equal(tmp_dir: Path, module_loader: ModuleLoader):
    with given:
        project_dir = tmp_dir
        path = project_dir / "scenarios" / "scenario.py"
        source1 = ScenarioSource(path, project_dir, module_loader)
        source2 = ScenarioSource(path, project_dir, module_loader)

    with when:
        result = source1 == source2

    with then:
        assert result is True


def test_sources_with_different_paths_not_equal(tmp_dir: Path, module_loader: ModuleLoader):
    with given:
        project_dir = tmp_dir
        path1 = project_dir / "scenarios" / "scenario1.py"
        path2 = project_dir / "scenarios" / "scenario2.py"
        source1 = ScenarioSource(path1, project_dir, module_loader)
        source2 = ScenarioSource(path2, project_dir, module_loader)

    with when:
        result = source1 == source2

    with then:
        assert result is False


def test_sources_with_different_project_dirs_not_equal(tmp_dir: Path, module_loader: ModuleLoader):
    with given:
        project_dir1 = tmp_dir / "project1"
        project_dir2 = tmp_dir / "project2"
        path = project_dir1 / "scenarios" / "scenario.py"
        source1 = ScenarioSource(path, project_dir1, module_loader)
        source2 = ScenarioSource(path, project_dir2, module_loader)

    with when:
        result = source1 == source2

    with then:
        assert result is False


def test_sources_with_different_module_loaders_not_equal(tmp_dir: Path):
    with given:
        project_dir = tmp_dir
        path = project_dir / "scenarios" / "scenario.py"
        source1 = ScenarioSource(path, project_dir, Mock(ModuleLoader))
        source2 = ScenarioSource(path, project_dir, Mock(ModuleLoader))

    with when:
        result = source1 == source2

    with then:
        assert result is False


def test_source_not_equal_to_other_object_types(tmp_dir: Path, module_loader: ModuleLoader):
    with given:
        project_dir = tmp_dir
        path = project_dir / "scenarios" / "scenario.py"
        source1 = ScenarioSource(path, project_dir, module_loader)

    with when:
        result = source1 == object()

    with then:
        assert result is False


def test_scenario_source_repr_shows_relevant_attrs(tmp_dir: Path, module_loader: ModuleLoader):
    with given:
        project_dir = tmp_dir
        path = project_dir / "scenarios" / "scenario.py"
        source = ScenarioSource(path, project_dir, module_loader)

    with when:
        repr_str = repr(source)

    with then:
        rel_path = path.relative_to(project_dir)
        assert repr_str == (
            f"ScenarioSource<path={rel_path!r}, project_dir={project_dir!r}), "
            f"module_loader={module_loader!r}>"
        )
