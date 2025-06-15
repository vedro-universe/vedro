from pathlib import Path
from textwrap import dedent

import pytest
from baby_steps import given, then, when

from vedro import Scenario
from vedro.core import ModuleLoader
from vedro.core.scenario_collector import ScenarioSource
from vedro.plugins.functioner import FuncBasedScenarioProvider as ScenarioProvider
from vedro.plugins.functioner import FunctionerPlugin

from ._utils import module_loader, provider, scenario_source, tmp_dir

__all__ = ("tmp_dir", "provider", "module_loader", "scenario_source",)  # fixtures


@pytest.mark.parametrize(("fn_def", "is_coro"), [
    ("def", False),
    ("async def", True),
])
async def test_func_scenario_detected(fn_def: str, is_coro: bool, *,
                                      provider: ScenarioProvider, scenario_source: ScenarioSource):
    with given:
        scenario_source.path.write_text(dedent(f'''
            from vedro import scenario
            @scenario
            {fn_def} create_user():
                pass
        '''))

    with when:
        scenarios = await provider.provide(scenario_source)

    with then:
        assert len(scenarios) == 1

        # scenario
        scenario = scenarios[0]
        assert scenario.subject == "create user"
        assert scenario.name == "create_user"
        assert scenario.unique_id == "scenarios/scenario.py::create_user"
        assert scenario.template_index is None
        assert scenario.template_total is None

        assert scenario.path == scenario_source.path
        assert scenario.rel_path == scenario_source.rel_path

        # steps
        assert len(scenario.steps) == 1
        assert scenario.steps[0].name == "do"
        assert scenario.steps[0].is_coro() is is_coro


async def test_parametrized_func_scenarios(provider: ScenarioProvider,
                                           scenario_source: ScenarioSource):
    with given:
        scenario_source.path.write_text(dedent('''
            from vedro import scenario, params
            @scenario([
                params(1),
                params(2)
            ])
            def create_user(user_id):
                pass
        '''))

    with when:
        scenarios = await provider.provide(scenario_source)

    with then:
        assert len(scenarios) == 2

        for idx, scenario in enumerate(scenarios, start=1):
            assert scenario.subject == "create user"
            assert scenario.name == "create_user"
            assert scenario.unique_id == f"scenarios/scenario.py::create_user#{idx}"
            assert scenario.template_index == idx
            assert scenario.template_total == 2

            assert scenario.path == scenario_source.path
            assert scenario.rel_path == scenario_source.rel_path

            # steps
            assert len(scenario.steps) == 1
            assert scenario.steps[0].name == "do"


@pytest.mark.parametrize("decorator", [
    "@scenario",
    "@scenario()",
])
async def test_scenario_decorator_variants(decorator: str, *, provider: ScenarioProvider,
                                           scenario_source: ScenarioSource):
    with given:
        scenario_source.path.write_text(dedent(f'''
            from vedro import scenario
            {decorator}
            def create_user():
                pass
        '''))

    with when:
        scenarios = await provider.provide(scenario_source)

    with then:
        assert len(scenarios) == 1


async def test_multiple_func_scenarios(provider: ScenarioProvider,
                                       scenario_source: ScenarioSource):
    with given:
        scenario_source.path.write_text(dedent('''
            from vedro import scenario
            @scenario
            def create_user():
                pass
            @scenario
            def update_user():
                pass
        '''))

    with when:
        scenarios = await provider.provide(scenario_source)

    with then:
        assert len(scenarios) == 2


async def test_undecorated_func_ignored(provider: ScenarioProvider,
                                        scenario_source: ScenarioSource):
    with given:
        scenario_source.path.write_text(dedent('''
            from vedro import scenario
            def create_user():
                pass
        '''))

    with when:
        scenarios = await provider.provide(scenario_source)

    with then:
        assert len(scenarios) == 0


async def test_private_func_ignored(provider: ScenarioProvider, scenario_source: ScenarioSource):
    with given:
        scenario_source.path.write_text(dedent('''
            from vedro import scenario
            @scenario
            def _create_user():
                pass
        '''))

    with when:
        scenarios = await provider.provide(scenario_source)

    with then:
        assert len(scenarios) == 0


async def test_empty_file_no_scenarios(provider: ScenarioProvider,
                                       scenario_source: ScenarioSource):
    with given:
        scenario_source.path.write_text("")

    with when:
        scenarios = await provider.provide(scenario_source)

    with then:
        assert len(scenarios) == 0


async def test_mixed_func_and_param_scenarios(provider: ScenarioProvider,
                                              scenario_source: ScenarioSource):
    with given:
        scenario_source.path.write_text(dedent('''
            from vedro import scenario, params

            @scenario
            def create_user():
                return 0

            @scenario([params(1), params(2)])
            def update_user(idx):
                return idx
        '''))

    with when:
        scenarios = await provider.provide(scenario_source)

    with then:
        assert len(scenarios) == 3
        for idx, scenario in enumerate(scenarios):
            scn = scenario()
            assert isinstance(scn, Scenario)

            assert scenario.steps[0](scn) == idx


async def test_async_func_and_param_scenarios(provider: ScenarioProvider,
                                              scenario_source: ScenarioSource):
    with given:
        scenario_source.path.write_text(dedent('''
            from vedro import scenario, params

            @scenario
            async def create_user():
                return 0

            @scenario([params(1), params(2)])
            async def update_user(idx):
                return idx
        '''))

    with when:
        scenarios = await provider.provide(scenario_source)

    with then:
        assert len(scenarios) == 3
        for idx, scenario in enumerate(scenarios):
            scn = scenario()
            assert isinstance(scn, Scenario)

            assert await scenario.steps[0](scn) == idx


async def test_ignore_non_python_scenario_files(provider: ScenarioProvider,
                                                tmp_dir: Path, module_loader: ModuleLoader):
    with given:
        path = tmp_dir / "scenarios" / "scenario.md"
        scenario_source_md = ScenarioSource(path, tmp_dir, module_loader)

    with when:
        scenarios = await provider.provide(scenario_source_md)

    with then:
        assert len(scenarios) == 0


async def test_custom_meta_on_scenario(provider: ScenarioProvider,
                                       scenario_source: ScenarioSource):
    with given:
        scenario_source.path.write_text(dedent('''
            from vedro.core import set_scenario_meta
            from vedro.plugins.functioner import FunctionerPlugin

            def scenario_decorator(key, value):
                def wrapper(scn):
                    set_scenario_meta(scn, key, value, plugin=FunctionerPlugin)
                    return scn
                return wrapper

            from vedro import scenario

            @scenario[
                scenario_decorator("decorated1", 1),
                scenario_decorator("decorated2", 2)
            ]
            def create_user():
                pass
        '''))

    with when:
        scenarios = await provider.provide(scenario_source)

    with then:
        assert len(scenarios) == 1

        scenario = scenarios[0]
        assert scenario.get_meta("decorated1", plugin=FunctionerPlugin) == 1
        assert scenario.get_meta("decorated2", plugin=FunctionerPlugin) == 2


async def test_custom_meta_on_parametrized_scenario(provider: ScenarioProvider,
                                                    scenario_source: ScenarioSource):
    with given:
        scenario_source.path.write_text(dedent('''
            from vedro.core import set_scenario_meta
            from vedro.plugins.functioner import FunctionerPlugin

            def scenario_decorator(key, value):
                def wrapper(scn):
                    set_scenario_meta(scn, key, value, plugin=FunctionerPlugin)
                    return scn
                return wrapper

            from vedro import scenario, params

            @scenario[
                scenario_decorator("decorated1", 1),
                scenario_decorator("decorated2", 2)
            ]([
                params('Bob'),
                params('Alice')
            ])
            def create_user(name):
                pass
        '''))

    with when:
        scenarios = await provider.provide(scenario_source)

    with then:
        assert len(scenarios) == 2

        for scenario in scenarios:
            assert scenario.get_meta("decorated1", plugin=FunctionerPlugin) == 1
            assert scenario.get_meta("decorated2", plugin=FunctionerPlugin) == 2
