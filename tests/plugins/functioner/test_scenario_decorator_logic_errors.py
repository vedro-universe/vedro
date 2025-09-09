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


async def test_decorating_callable_class_instance(provider: ScenarioProvider,
                                                  scenario_source: ScenarioSource):
    with given:
        scenario_source.path.write_text(dedent('''
            from vedro import scenario

            class MyCallable:
                def __call__(self):
                    pass

            obj = MyCallable()

            scenario()(obj)
        ''').strip())

    with when, raises(BaseException) as exc:
        await provider.provide(scenario_source)

    with then:
        assert exc.type is TypeError
        assert str(exc.value) == (
            "@scenario can only be applied to regular functions"
        )


async def test_decorating_builtin_function(provider: ScenarioProvider,
                                           scenario_source: ScenarioSource):
    with given:
        scenario_source.path.write_text(dedent('''
            from vedro import scenario

            scenario()(len)
        ''').strip())

    with when, raises(BaseException) as exc:
        await provider.provide(scenario_source)

    with then:
        assert exc.type is TypeError
        assert str(exc.value) == (
            "@scenario can only be applied to regular functions"
        )


async def test_shadowing_decorated_function(provider: ScenarioProvider,
                                            scenario_source: ScenarioSource):
    with given:
        scenario_source.path.write_text(dedent('''
            from vedro import scenario

            def update_user():
                print("User updated")

            @scenario()
            def update_user():
                pass  # Can't call update_user() here as it would be shadowed

            # This will fail because update_user is now a ScenarioDescriptor, not callable
            print(update_user())
        ''').strip())

    with when, raises(BaseException) as exc:
        await provider.provide(scenario_source)

    with then:
        assert exc.type is TypeError
        assert str(exc.value) == "'ScenarioDescriptor' object is not callable"


async def test_anonymous_function_overwrites_sanitized_name(provider: ScenarioProvider,
                                                            scenario_source: ScenarioSource):
    with given:
        scenario_source.path.write_text(dedent('''
            from vedro import scenario

            def update_user():
                return "original"

            @scenario("update user")
            def _():
                pass

            # update_user is now overwritten with ScenarioDescriptor
            # because "update user" sanitizes to "update_user"
            print(update_user())  # This will fail
        ''').strip())

    with when, raises(BaseException) as exc:
        await provider.provide(scenario_source)

    with then:
        assert exc.type is TypeError
        assert str(exc.value) == "'ScenarioDescriptor' object is not callable"


async def test_function_starting_with_underscore_without_subject(provider: ScenarioProvider,
                                                                 scenario_source: ScenarioSource):
    with given:
        scenario_source.path.write_text(dedent('''
            from vedro import scenario

            @scenario()
            def _fn():
                pass
        ''').strip())

    with when:
        scenarios = await provider.provide(scenario_source)

    with then:
        # Functions starting with underscore (except anonymous _) are ignored by the provider
        assert len(scenarios) == 0


async def test_function_starting_with_underscore_with_subject(provider: ScenarioProvider,
                                                              scenario_source: ScenarioSource):
    with given:
        scenario_source.path.write_text(dedent('''
            from vedro import scenario

            @scenario("subject")
            def _fn():
                pass
        ''').strip())

    with when:
        scenarios = await provider.provide(scenario_source)

    with then:
        # Functions starting with underscore (except anonymous _) are ignored by the provider
        assert len(scenarios) == 0
