from unittest.mock import MagicMock

import pytest
from baby_steps import given, then, when
from pytest import raises

from vedro import computed
from vedro.commands.run_command._plugin_registrar import PluginRegistrar
from vedro.core import Dispatcher, Plugin, PluginConfig


@pytest.fixture()
def registrar() -> PluginRegistrar:
    return PluginRegistrar()


@pytest.fixture()
def dispatcher_() -> Dispatcher:
    return MagicMock(spec=Dispatcher)


class CustomPlugin(Plugin):
    pass


class CustomPluginConfig(PluginConfig):
    plugin = CustomPlugin


def test_register_no_plugins(*, registrar: PluginRegistrar, dispatcher_: Dispatcher):
    with given:
        plugins = []

    with when:
        res = registrar.register(plugins, dispatcher_)

    with then:
        assert res is None
        assert dispatcher_.register.mock_calls == []


def test_register_plugins_no_deps(*, registrar: PluginRegistrar, dispatcher_: Dispatcher):
    with given:
        class AnotherPluginConfig(PluginConfig):
            plugin = CustomPlugin

        plugins = [AnotherPluginConfig, CustomPluginConfig]

    with when:
        registrar.register(plugins, dispatcher_)

    with then:
        assert len(dispatcher_.register.mock_calls) == 2

        registered_plugin1 = dispatcher_.register.mock_calls[0].args[0]
        assert isinstance(registered_plugin1, CustomPlugin)
        assert registered_plugin1.config is AnotherPluginConfig

        registered_plugin2 = dispatcher_.register.mock_calls[1].args[0]
        assert isinstance(registered_plugin2, CustomPlugin)
        assert registered_plugin2.config is CustomPluginConfig


def test_register_plugins_skip_disabled(*, registrar: PluginRegistrar, dispatcher_: Dispatcher):
    with given:
        class AnotherPluginConfig(PluginConfig):
            plugin = CustomPlugin
            enabled = False

        plugins = [CustomPluginConfig, AnotherPluginConfig]

    with when:
        registrar.register(plugins, dispatcher_)

    with then:
        assert len(dispatcher_.register.mock_calls) == 1

        registered_plugin = dispatcher_.register.mock_calls[0].args[0]
        assert isinstance(registered_plugin, CustomPlugin)
        assert registered_plugin.config is CustomPluginConfig


def test_register_plugins_with_deps(*, registrar: PluginRegistrar, dispatcher_: Dispatcher):
    with given:
        class AnotherPluginConfig(PluginConfig):
            plugin = CustomPlugin
            depends_on = [CustomPluginConfig]

        plugins = [AnotherPluginConfig, CustomPluginConfig]

    with when:
        registrar.register(plugins, dispatcher_)

    with then:
        assert len(dispatcher_.register.mock_calls) == 2

        registered_plugin1 = dispatcher_.register.mock_calls[0].args[0]
        assert isinstance(registered_plugin1, CustomPlugin)
        assert registered_plugin1.config is CustomPluginConfig

        registered_plugin2 = dispatcher_.register.mock_calls[1].args[0]
        assert isinstance(registered_plugin2, CustomPlugin)
        assert registered_plugin2.config is AnotherPluginConfig


def test_register_plugins_with_deps_cycle(*, registrar: PluginRegistrar, dispatcher_: Dispatcher):
    with given:
        class AnotherPluginConfig(PluginConfig):
            plugin = CustomPlugin
            depends_on = computed(lambda _: [CustomPluginConfig, CyclePluginConfig])

        class CyclePluginConfig(PluginConfig):
            plugin = CustomPlugin
            depends_on = [AnotherPluginConfig]

        plugins = [CustomPluginConfig, AnotherPluginConfig, CyclePluginConfig]

    with when, raises(BaseException) as exc:
        registrar.register(plugins, dispatcher_)

    with then:
        assert exc.type is RuntimeError
        assert str(exc.value) == "Cycle detected in plugin dependencies"

        assert dispatcher_.register.mock_calls == []


def test_register_plugins_complex_dependency_graph(*, registrar: PluginRegistrar,
                                                   dispatcher_: Dispatcher):
    with given:
        class A(PluginConfig):
            plugin = CustomPlugin
            depends_on = computed(lambda _: [B, C])

        class B(PluginConfig):
            plugin = CustomPlugin
            depends_on = computed(lambda _: [D])

        class C(PluginConfig):
            plugin = CustomPlugin
            depends_on = computed(lambda _: [])

        class D(PluginConfig):
            plugin = CustomPlugin
            depends_on = computed(lambda _: [E])

        class E(PluginConfig):
            plugin = CustomPlugin
            depends_on = computed(lambda _: [])

        plugins = [A, B, C, D, E]

    with when:
        registrar.register(plugins, dispatcher_)

    with then:
        assert len(dispatcher_.register.mock_calls) == 5

        for plugin_config in [C, E, D, B, A]:
            registered_plugin = dispatcher_.register.mock_calls.pop(0).args[0]
            assert isinstance(registered_plugin, CustomPlugin)
            assert registered_plugin.config is plugin_config
