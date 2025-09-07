from textwrap import dedent

from baby_steps import given, then, when
from pytest import raises

from vedro.core.scenario_collector import ScenarioSource
from vedro.plugins.functioner import FuncBasedScenarioProvider as ScenarioProvider
from vedro.plugins.functioner._errors import DuplicateScenarioError

from ._utils import module_loader, provider, scenario_source, tmp_dir

__all__ = ("tmp_dir", "provider", "module_loader", "scenario_source",)  # fixtures


async def test_duplicate_function_name_error(provider: ScenarioProvider,
                                             scenario_source: ScenarioSource):
    with given:
        scenario_source.path.write_text(dedent('''
            from vedro import scenario

            @scenario
            def create_user():
                pass

            @scenario
            def create_user():
                pass
        ''').strip())

    with when:
        with raises(BaseException) as exc:
            await provider.provide(scenario_source)

    with then:
        assert exc.type is DuplicateScenarioError
        assert str(exc.value) == (
            "Duplicate scenario function 'create_user' found. "
            "Each scenario function must have a unique name."
        )


async def test_duplicate_subject_for_anonymous_functions(provider: ScenarioProvider,
                                                         scenario_source: ScenarioSource):
    with given:
        scenario_source.path.write_text(dedent('''
            from vedro import scenario

            @scenario("update user")
            def _():
                pass

            @scenario("update user")
            def _():
                pass
        ''').strip())

    with when:
        with raises(BaseException) as exc:
            await provider.provide(scenario_source)

    with then:
        assert exc.type is DuplicateScenarioError
        assert str(exc.value) == (
            "Duplicate scenario with subject 'update user' found. "
            "Each anonymous scenario must have a unique subject."
        )


async def test_anonymous_function_without_subject(provider: ScenarioProvider,
                                                  scenario_source: ScenarioSource):
    with given:
        scenario_source.path.write_text(dedent('''
            from vedro import scenario

            @scenario
            def _():
                pass
        ''').strip())

    with when:
        with raises(BaseException) as exc:
            await provider.provide(scenario_source)

    with then:
        assert exc.type is DuplicateScenarioError
        assert str(exc.value) == (
            "Anonymous scenario function '_' requires a subject. "
            "Use @scenario('subject') to provide one."
        )
