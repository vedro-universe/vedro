from pathlib import Path
from textwrap import dedent

import pytest
from baby_steps import given, then, when
from pytest import raises

from vedro.core import ModuleFileLoader, ModuleLoader
from vedro.core.scenario_collector import ClassBasedScenarioProvider, ScenarioSource

from ._utils import tmp_dir

__all__ = ("tmp_dir",)  # fixtures


@pytest.fixture()
def module_loader() -> ModuleLoader:
    return ModuleFileLoader()


@pytest.fixture()
def provider() -> ClassBasedScenarioProvider:
    return ClassBasedScenarioProvider()


@pytest.fixture()
def scenario_source(tmp_dir: Path, module_loader: ModuleLoader) -> ScenarioSource:
    project_dir = tmp_dir
    path = project_dir / "scenarios" / "scenario.py"
    return ScenarioSource(path, project_dir, module_loader)


@pytest.mark.parametrize("name", [
    "Scenario",  # default
    "TmpScenario",  # custom name (prefix)
    "ScenarioTmp",  # custom name (suffix)
    "Scenario_1",  # backward compatibility
    "Scenario_1_VedroScenario",  # parametrized
])
async def test_single_scenario_with_various_class_names(name, *,
                                                        provider: ClassBasedScenarioProvider,
                                                        scenario_source: ScenarioSource):
    with given:
        scenario_source.path.write_text(dedent(f'''
            import vedro
            class {name}(vedro.Scenario):
                pass
        '''))

    with when:
        scenarios = await provider.provide(scenario_source)

    with then:
        assert len(scenarios) == 1


async def test_multiple_scenarios_in_one_module(provider: ClassBasedScenarioProvider,
                                                scenario_source: ScenarioSource):
    with given:
        scenario_source.path.write_text(dedent('''
            import vedro
            class CreateUserScenario(vedro.Scenario):
                pass
            class UpdatedUserScenario(vedro.Scenario):
                pass
        '''))

    with when:
        scenarios = await provider.provide(scenario_source)

    with then:
        assert len(scenarios) == 2


async def test_parametrized_scenarios(provider: ClassBasedScenarioProvider,
                                      scenario_source: ScenarioSource):
    with given:
        scenario_source.path.write_text(dedent('''
            import vedro
            class Scenario(vedro.Scenario):
                @vedro.params("Bob")
                @vedro.params("Alice")
                def __init__(self, user):
                    pass
        '''))

    with when:
        scenarios = await provider.provide(scenario_source)

    with then:
        assert len(scenarios) == 2


async def test_error_on_non_inheriting_scenario_class(provider: ClassBasedScenarioProvider,
                                                      scenario_source: ScenarioSource):
    with given:
        scenario_source.path.write_text(dedent('''
            class Scenario:
                pass
        '''))

    with when, raises(BaseException) as exc:
        await provider.provide(scenario_source)

    with then:
        assert exc.type is TypeError
        assert str(exc.value) == "'scenarios.scenario.Scenario' must inherit from 'vedro.Scenario'"


async def test_no_scenarios_in_empty_file(provider: ClassBasedScenarioProvider,
                                          scenario_source: ScenarioSource):
    with given:
        scenario_source.path.write_text("")

    with when:
        scenarios = await provider.provide(scenario_source)

    with then:
        assert len(scenarios) == 0


async def test_detect_only_scenario_classes_among_others(provider: ClassBasedScenarioProvider,
                                                         scenario_source: ScenarioSource):
    with given:
        scenario_source.path.write_text(dedent('''
            import vedro
            class User:
                pass
            class Scenario(vedro.Scenario):
                pass
        '''))

    with when:
        scenarios = await provider.provide(scenario_source)

    with then:
        assert len(scenarios) == 1


async def test_ignore_function_named_scenario(provider: ClassBasedScenarioProvider,
                                              scenario_source: ScenarioSource):
    with given:
        scenario_source.path.write_text(dedent('''
            import vedro
            class UserScenario(vedro.Scenario):
                pass
            def Scenario():
                pass
        '''))

    with when:
        scenarios = await provider.provide(scenario_source)

    with then:
        assert len(scenarios) == 1


async def test_ignore_non_python_scenario_files(provider: ClassBasedScenarioProvider,
                                                tmp_dir: Path, module_loader: ModuleLoader):
    with given:
        path = tmp_dir / "scenarios" / "scenario.md"
        scenario_source_md = ScenarioSource(path, tmp_dir, module_loader)

    with when:
        scenarios = await provider.provide(scenario_source_md)

    with then:
        assert len(scenarios) == 0
