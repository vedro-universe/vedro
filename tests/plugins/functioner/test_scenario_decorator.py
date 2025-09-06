from textwrap import dedent

from baby_steps import given, then, when

from vedro.core.scenario_collector import ScenarioSource
from vedro.plugins.functioner import FuncBasedScenarioProvider as ScenarioProvider

from ._utils import get_scenario_tags, module_loader, provider, scenario_source, tmp_dir

__all__ = ("tmp_dir", "provider", "module_loader", "scenario_source",)  # fixtures


# Basic patterns

async def test_direct_decoration(provider: ScenarioProvider, scenario_source: ScenarioSource):
    with given:
        scenario_source.path.write_text(dedent('''
            from vedro import scenario, params

            @scenario
            def create_user():
                pass
        ''').strip())

    with when:
        scenarios = await provider.provide(scenario_source)

    with then:
        assert len(scenarios) == 1
        assert scenarios[0].subject == "create user"
        assert scenarios[0].name == "create_user"
        assert get_scenario_tags(scenarios[0]) == ()


async def test_empty_call(provider: ScenarioProvider, scenario_source: ScenarioSource):
    with given:
        scenario_source.path.write_text(dedent('''
            from vedro import scenario, params

            @scenario()
            def create_user():
                pass
        ''').strip())

    with when:
        scenarios = await provider.provide(scenario_source)

    with then:
        assert len(scenarios) == 1
        assert scenarios[0].subject == "create user"
        assert scenarios[0].name == "create_user"
        assert get_scenario_tags(scenarios[0]) == ()


# Single argument patterns


async def test_parameterization_positional(provider: ScenarioProvider, 
                                          scenario_source: ScenarioSource):
    with given:
        scenario_source.path.write_text(dedent('''
            from vedro import scenario, params

            @scenario([
                params(1),
                params(2),
            ])
            def create_user(idx: int):
                pass
        ''').strip())

    with when:
        scenarios = await provider.provide(scenario_source)

    with then:
        assert len(scenarios) == 2
        for idx, scn in enumerate(scenarios, start=1):
            assert scn.subject == "create user"
            assert scn.name == "create_user"
            assert scn.template_index == idx
            assert scn.template_total == 2
            assert scn._orig_scenario.tags == ()


async def test_parameterization_keyword(provider: ScenarioProvider,
                                       scenario_source: ScenarioSource):
    with given:
        scenario_source.path.write_text(dedent('''
            from vedro import scenario, params

            @scenario(cases=[
                params(1),
                params(2),
            ])
            def create_user(idx: int):
                pass
        ''').strip())

    with when:
        scenarios = await provider.provide(scenario_source)

    with then:
        assert len(scenarios) == 2
        for idx, scn in enumerate(scenarios, start=1):
            assert scn.subject == "create user"
            assert scn.name == "create_user"
            assert scn.template_index == idx
            assert scn.template_total == 2
            assert scn._orig_scenario.tags == ()


async def test_subject_positional(provider: ScenarioProvider, scenario_source: ScenarioSource):
    with given:
        scenario_source.path.write_text(dedent('''
            from vedro import scenario, params

            @scenario("create user")
            def _():
                pass
        ''').strip())

    with when:
        scenarios = await provider.provide(scenario_source)

    with then:
        assert len(scenarios) == 1
        assert scenarios[0].subject == "create user"
        assert scenarios[0].name == "_"
        assert get_scenario_tags(scenarios[0]) == ()


async def test_subject_keyword(provider: ScenarioProvider, scenario_source: ScenarioSource):
    with given:
        scenario_source.path.write_text(dedent('''
            from vedro import scenario, params

            @scenario(subject="create user")
            def _():
                pass
        ''').strip())

    with when:
        scenarios = await provider.provide(scenario_source)

    with then:
        assert len(scenarios) == 1
        assert scenarios[0].subject == "create user"
        assert scenarios[0].name == "_"
        assert get_scenario_tags(scenarios[0]) == ()


async def test_tags_only_keyword(provider: ScenarioProvider, scenario_source: ScenarioSource):
    with given:
        scenario_source.path.write_text(dedent('''
            from vedro import scenario, params

            @scenario(tags={"API", "P0"})
            def create_user():
                pass
        ''').strip())

    with when:
        scenarios = await provider.provide(scenario_source)

    with then:
        assert len(scenarios) == 1
        assert scenarios[0].subject == "create user"
        assert scenarios[0].name == "create_user"
        assert get_scenario_tags(scenarios[0]) == {"API", "P0"}


# Two argument patterns


async def test_subject_params_both_positional(provider: ScenarioProvider,
                                              scenario_source: ScenarioSource):
    with given:
        scenario_source.path.write_text(dedent('''
            from vedro import scenario, params

            @scenario("create user", [
                params(idx=1),
                params(idx=2),
            ])
            def _(idx: int):
                pass
        ''').strip())

    with when:
        scenarios = await provider.provide(scenario_source)

    with then:
        assert len(scenarios) == 2
        for idx, scn in enumerate(scenarios, start=1):
            assert scn.subject == "create user"
            assert scn.name == "_"
            assert scn.template_index == idx
            assert scn.template_total == 2
            assert scn._orig_scenario.tags == ()


async def test_subject_positional_cases_keyword(provider: ScenarioProvider,
                                               scenario_source: ScenarioSource):
    with given:
        scenario_source.path.write_text(dedent('''
            from vedro import scenario, params

            @scenario("create user", cases=[
                params(idx=1),
                params(idx=2),
            ])
            def _(idx: int):
                pass
        ''').strip())

    with when:
        scenarios = await provider.provide(scenario_source)

    with then:
        assert len(scenarios) == 2
        for idx, scn in enumerate(scenarios, start=1):
            assert scn.subject == "create user"
            assert scn.name == "_"
            assert scn.template_index == idx
            assert scn.template_total == 2
            assert scn._orig_scenario.tags == ()


async def test_subject_positional_tags_keyword(provider: ScenarioProvider,
                                              scenario_source: ScenarioSource):
    with given:
        scenario_source.path.write_text(dedent('''
            from vedro import scenario, params

            @scenario("create user", tags={"API", "P0"})
            def _():
                pass
        ''').strip())

    with when:
        scenarios = await provider.provide(scenario_source)

    with then:
        assert len(scenarios) == 1
        assert scenarios[0].subject == "create user"
        assert scenarios[0].name == "_"
        assert get_scenario_tags(scenarios[0]) == {"API", "P0"}


async def test_subject_cases_both_keywords(provider: ScenarioProvider,
                                          scenario_source: ScenarioSource):
    with given:
        scenario_source.path.write_text(dedent('''
            from vedro import scenario, params

            @scenario(subject="create user", cases=[
                params(idx=1),
                params(idx=2),
            ])
            def _(idx: int):
                pass
        ''').strip())

    with when:
        scenarios = await provider.provide(scenario_source)

    with then:
        assert len(scenarios) == 2
        for idx, scn in enumerate(scenarios, start=1):
            assert scn.subject == "create user"
            assert scn.name == "_"
            assert scn.template_index == idx
            assert scn.template_total == 2
            assert scn._orig_scenario.tags == ()


async def test_subject_tags_both_keywords(provider: ScenarioProvider,
                                         scenario_source: ScenarioSource):
    with given:
        scenario_source.path.write_text(dedent('''
            from vedro import scenario, params

            @scenario(subject="create user", tags={"API", "P0"})
            def _():
                pass
        ''').strip())

    with when:
        scenarios = await provider.provide(scenario_source)

    with then:
        assert len(scenarios) == 1
        assert scenarios[0].subject == "create user"
        assert scenarios[0].name == "_"
        assert get_scenario_tags(scenarios[0]) == {"API", "P0"}


async def test_cases_tags_both_keywords(provider: ScenarioProvider,
                                       scenario_source: ScenarioSource):
    with given:
        scenario_source.path.write_text(dedent('''
            from vedro import scenario, params

            @scenario(cases=[params(idx=1)], tags={"API"})
            def create_user(idx: int):
                pass
        ''').strip())

    with when:
        scenarios = await provider.provide(scenario_source)

    with then:
        assert len(scenarios) == 1
        assert scenarios[0].subject == "create user"
        assert scenarios[0].name == "create_user"
        assert scenarios[0].template_index == 1
        assert scenarios[0].template_total == 1
        assert get_scenario_tags(scenarios[0]) == {"API"}


async def test_params_positional_tags_keyword(provider: ScenarioProvider,
                                             scenario_source: ScenarioSource):
    with given:
        scenario_source.path.write_text(dedent('''
            from vedro import scenario, params

            @scenario([params(idx=1)], tags={"API"})
            def create_user(idx: int):
                pass
        ''').strip())

    with when:
        scenarios = await provider.provide(scenario_source)

    with then:
        assert len(scenarios) == 1
        assert scenarios[0].subject == "create user"
        assert scenarios[0].name == "create_user"
        assert scenarios[0].template_index == 1
        assert scenarios[0].template_total == 1
        assert get_scenario_tags(scenarios[0]) == {"API"}


# Three argument patterns


async def test_subject_params_positional_tags_keyword(provider: ScenarioProvider,
                                                      scenario_source: ScenarioSource):
    with given:
        scenario_source.path.write_text(dedent('''
            from vedro import scenario, params

            @scenario("create user", [params(idx=1)], tags={"API", "P0"})
            def _(idx: int):
                pass
        ''').strip())

    with when:
        scenarios = await provider.provide(scenario_source)

    with then:
        assert len(scenarios) == 1
        assert scenarios[0].subject == "create user"
        assert scenarios[0].name == "_"
        assert scenarios[0].template_index == 1
        assert scenarios[0].template_total == 1
        assert get_scenario_tags(scenarios[0]) == {"API", "P0"}


async def test_subject_positional_cases_tags_keywords(provider: ScenarioProvider,
                                                      scenario_source: ScenarioSource):
    with given:
        scenario_source.path.write_text(dedent('''
            from vedro import scenario, params

            @scenario("create user", cases=[params(idx=1)], tags={"API", "P0"})
            def _(idx: int):
                pass
        ''').strip())

    with when:
        scenarios = await provider.provide(scenario_source)

    with then:
        assert len(scenarios) == 1
        assert scenarios[0].subject == "create user"
        assert scenarios[0].name == "_"
        assert scenarios[0].template_index == 1
        assert scenarios[0].template_total == 1
        assert get_scenario_tags(scenarios[0]) == {"API", "P0"}


async def test_subject_cases_tags_all_keywords(provider: ScenarioProvider,
                                              scenario_source: ScenarioSource):
    with given:
        scenario_source.path.write_text(dedent('''
            from vedro import scenario, params

            @scenario(subject="create user", cases=[params(idx=1)], tags={"API"})
            def _(idx: int):
                pass
        ''').strip())

    with when:
        scenarios = await provider.provide(scenario_source)

    with then:
        assert len(scenarios) == 1
        assert scenarios[0].subject == "create user"
        assert scenarios[0].name == "_"
        assert scenarios[0].template_index == 1
        assert scenarios[0].template_total == 1
        assert get_scenario_tags(scenarios[0]) == {"API"}
