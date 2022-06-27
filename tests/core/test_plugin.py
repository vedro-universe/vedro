from baby_steps import given, then, when
from pytest import raises

from vedro.core import Dispatcher, Plugin, PluginConfig, Section


def test_plugin_get_config():
    with given:
        config = PluginConfig
        plugin = Plugin(config)

    with when:
        res = plugin.config

    with then:
        assert res == config


def test_plugin_incorrect_config():
    with when, raises(BaseException) as exc:
        Plugin(Section)

    with then:
        assert exc.type is AssertionError


def test_plugin_subscribe():
    with given:
        dispatcher = Dispatcher()
        plugin = Plugin(PluginConfig)

    with when:
        res = plugin.subscribe(dispatcher)

    with then:
        assert res is None


def test_config_get_plugin():
    with given:
        config = PluginConfig

    with when:
        res = config.plugin

    with then:
        assert res == Plugin


def test_config_get_enabled():
    with given:
        config = PluginConfig

    with when:
        res = config.enabled

    with then:
        assert res is True
