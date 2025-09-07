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


async def test_decorator_function_with_extra_decorator_args(provider: ScenarioProvider,
                                                            scenario_source: ScenarioSource):
    with given:
        scenario_source.path.write_text(dedent('''
            from vedro import scenario

            def fn():
                pass

            scenario()(fn, "extra_arg")
        ''').strip())

    with when, raises(BaseException) as exc:
        await provider.provide(scenario_source)

    with then:
        assert exc.type is TypeError
        assert str(exc.value) == (
            "@scenario() takes 1 positional argument when decorating a function but 2 were given"
            " with 0 keyword arguments"
        )


async def test_invalid_first_positional_arg(provider: ScenarioProvider,
                                            scenario_source: ScenarioSource):
    with given:
        scenario_source.path.write_text(dedent('''
            from vedro import scenario

            @scenario(123)
            def create_user():
                pass
        ''').strip())

    with when, raises(BaseException) as exc:
        await provider.provide(scenario_source)

    with then:
        assert exc.type is TypeError
        assert str(exc.value) == (
            "First positional argument must be either str (subject) or list/tuple (cases), got int"
        )


async def test_two_args_first_not_string(provider: ScenarioProvider,
                                         scenario_source: ScenarioSource):
    with given:
        scenario_source.path.write_text(dedent('''
            from vedro import scenario, params

            @scenario(123, [params(1), params(2)])
            def create_user(idx):
                pass
        ''').strip())

    with when, raises(BaseException) as exc:
        await provider.provide(scenario_source)

    with then:
        assert exc.type is TypeError
        assert str(exc.value) == (
            "When providing two positional arguments, first must be str (subject), got int"
        )


async def test_two_args_second_not_list(provider: ScenarioProvider,
                                        scenario_source: ScenarioSource):
    with given:
        scenario_source.path.write_text(dedent('''
            from vedro import scenario

            @scenario("subject", "not_a_list")
            def create_user():
                pass
        ''').strip())

    with when, raises(BaseException) as exc:
        await provider.provide(scenario_source)

    with then:
        assert exc.type is TypeError
        assert str(exc.value) == (
            "When providing two positional arguments, second must be list or "
            "tuple (cases), got str"
        )


async def test_too_many_positional_args(provider: ScenarioProvider,
                                        scenario_source: ScenarioSource):
    with given:
        scenario_source.path.write_text(dedent('''
            from vedro import scenario, params

            @scenario("subject", [params(1), params(2)], "extra")
            def create_user():
                pass
        ''').strip())

    with when, raises(BaseException) as exc:
        await provider.provide(scenario_source)

    with then:
        assert exc.type is TypeError
        assert str(exc.value) == "@scenario() takes at most 2 positional arguments (3 given)"


async def test_multiple_values_for_subject(provider: ScenarioProvider,
                                           scenario_source: ScenarioSource):
    with given:
        scenario_source.path.write_text(dedent('''
            from vedro import scenario

            @scenario("positional_subject", subject="keyword_subject")
            def create_user():
                pass
        ''').strip())

    with when, raises(BaseException) as exc:
        await provider.provide(scenario_source)

    with then:
        assert exc.type is TypeError
        assert str(exc.value) == "Got multiple values for argument 'subject'"


async def test_invalid_subject_type(provider: ScenarioProvider,
                                    scenario_source: ScenarioSource):
    with given:
        scenario_source.path.write_text(dedent('''
            from vedro import scenario

            @scenario(subject=123)
            def create_user():
                pass
        ''').strip())

    with when, raises(BaseException) as exc:
        await provider.provide(scenario_source)

    with then:
        assert exc.type is TypeError
        assert str(exc.value) == "subject must be str or None, got int"


async def test_multiple_values_for_cases(provider: ScenarioProvider,
                                         scenario_source: ScenarioSource):
    with given:
        scenario_source.path.write_text(dedent('''
            from vedro import scenario, params

            @scenario([params(1)], cases=[params(2)])
            def create_user(idx):
                pass
        ''').strip())

    with when, raises(BaseException) as exc:
        await provider.provide(scenario_source)

    with then:
        assert exc.type is TypeError
        assert str(exc.value) == "Got multiple values for argument 'cases'"


async def test_invalid_cases_type(provider: ScenarioProvider,
                                  scenario_source: ScenarioSource):
    with given:
        scenario_source.path.write_text(dedent('''
            from vedro import scenario

            @scenario(cases="not_a_list")
            def create_user():
                pass
        ''').strip())

    with when, raises(BaseException) as exc:
        await provider.provide(scenario_source)

    with then:
        assert exc.type is TypeError
        assert str(exc.value) == "cases must be list or tuple, got str"


async def test_invalid_tags_type(provider: ScenarioProvider,
                                 scenario_source: ScenarioSource):
    with given:
        scenario_source.path.write_text(dedent('''
            from vedro import scenario

            @scenario(tags="not_a_list")
            def create_user():
                pass
        ''').strip())

    with when, raises(BaseException) as exc:
        await provider.provide(scenario_source)

    with then:
        assert exc.type is TypeError
        assert str(exc.value) == "tags must be list, tuple, or set, got str"


async def test_unexpected_keyword_args(provider: ScenarioProvider,
                                       scenario_source: ScenarioSource):
    with given:
        scenario_source.path.write_text(dedent('''
            from vedro import scenario

            @scenario(unexpected="value", another="arg")
            def create_user():
                pass
        ''').strip())

    with when, raises(BaseException) as exc:
        await provider.provide(scenario_source)

    with then:
        assert exc.type is TypeError
        assert str(exc.value) == (
            "@scenario() got unexpected keyword argument(s): another, unexpected"
        )
