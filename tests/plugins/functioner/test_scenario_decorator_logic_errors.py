from textwrap import dedent

from baby_steps import given, then, when
from pytest import raises

from vedro.core.scenario_collector import ScenarioSource
from vedro.plugins.functioner import FuncBasedScenarioProvider as ScenarioProvider
from vedro.plugins.functioner._errors import (
    AnonymousScenarioError,
    DuplicateScenarioError,
    FunctionShadowingError,
    ScenarioDeclarationError,
)

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
            "Found duplicate scenario 'create_user' at 'scenarios/scenario.py:7'. "
            "Please rename one of the scenarios to have a unique name."
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
            "Multiple scenarios found with subject 'update user' at 'scenarios/scenario.py:7'. "
            "When using anonymous functions (like '_'), each must have a unique subject. "
            "Consider renaming one or using named functions instead."
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
        assert exc.type is AnonymousScenarioError
        assert str(exc.value) == (
            "Scenario function '_' at 'scenarios/scenario.py:3' needs a subject. "
            "Add one like this: @scenario('your subject here')"
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
        assert exc.type is ScenarioDeclarationError
        assert str(exc.value) == (
            "@scenario decorator cannot be used on MyCallable in module 'scenarios.scenario'. "
            "It can only decorate regular functions defined with 'def' or 'async def'."
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
        assert exc.type is ScenarioDeclarationError
        assert str(exc.value) == (
            "@scenario decorator cannot be used on 'len' (builtin_function_or_method) "
            "in module 'builtins'. "
            "It can only decorate regular functions defined with 'def' or 'async def'."
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
                pass
        ''').strip())

    with when, raises(BaseException) as exc:
        await provider.provide(scenario_source)

    with then:
        assert exc.type is FunctionShadowingError
        assert str(exc.value) == (
            "Scenario 'update_user' at 'scenarios/scenario.py:6' conflicts with an existing "
            "function. "
            "Please either: 1) Rename your scenario function, or 2) Rename the existing function"
        )


async def test_anonymous_function_overwrites_sanitized_name(provider: ScenarioProvider,
                                                            scenario_source: ScenarioSource):
    with given:
        scenario_source.path.write_text(dedent('''
            from vedro import scenario

            def update_user():
                print("User updated")

            @scenario("update user")
            def _():
                pass
        ''').strip())

    with when, raises(BaseException) as exc:
        await provider.provide(scenario_source)

    with then:
        assert exc.type is FunctionShadowingError
        assert str(exc.value) == (
            "Subject 'update user' at 'scenarios/scenario.py:6' would create a conflict with "
            "existing function 'update_user'. "
            "Please either: 1) Choose a different subject, or 2) Rename the existing function"
        )


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


async def test_scenario_descriptor_set_name_raises_error(provider: ScenarioProvider,
                                                         scenario_source: ScenarioSource):
    with given:
        scenario_source.path.write_text(dedent('''
            from vedro import scenario

            class MyClass:
                @scenario
                def test_method(self):
                    pass
        ''').strip())

    with when:
        with raises(BaseException) as exc:
            await provider.provide(scenario_source)

    with then:
        assert exc.type is ScenarioDeclarationError
        assert str(exc.value) == (
            "@scenario decorator cannot be used on method 'test_method' in class 'MyClass'. "
            "Scenarios must be module-level functions, not class methods."
        )
