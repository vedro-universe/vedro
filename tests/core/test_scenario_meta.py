import pytest
from baby_steps import given, then, when
from pytest import raises

from vedro import Scenario
from vedro.core import Plugin, PluginConfig
from vedro.core._scenario_meta import (
    _get_meta_key,
    _get_plugin_name,
    _validate_key,
    _validate_plugin,
    _validate_scenario,
)


def test_get_plugin_class_name():
    with given:
        class CustomPlugin(Plugin):
            pass

    with when:
        name = _get_plugin_name(CustomPlugin)

    with then:
        assert name == f"{CustomPlugin.__module__}.{CustomPlugin.__name__}"


def test_get_plugin_instance_name():
    with given:
        class CustomPlugin(Plugin):
            pass

    with when:
        name = _get_plugin_name(CustomPlugin(PluginConfig))

    with then:
        assert name == f"{CustomPlugin.__module__}.{CustomPlugin.__name__}"


def test_get_meta_key():
    with given:
        class CustomPlugin(Plugin):
            pass

        namespace = _get_plugin_name(CustomPlugin)

    with when:
        key = _get_meta_key(CustomPlugin, "key")

    with then:
        assert key == f"{namespace}.key"


def test_validate_plugin_class():
    with given:
        class CustomPlugin(Plugin):
            pass

    with when:
        res = _validate_plugin(CustomPlugin)

    with then:
        assert res is True


def test_validate_plugin_instance():
    with given:
        class CustomPlugin(Plugin):
            pass

    with when:
        res = _validate_plugin(CustomPlugin(PluginConfig))

    with then:
        assert res is True


def test_validate_plugin_invalid():
    with given:
        class CustomPlugin:
            pass

    with when, raises(Exception) as exc:
        _validate_plugin(CustomPlugin)

    with then:
        assert exc.type is TypeError
        assert str(exc.value) == "`plugin` must be a Plugin instance or a subclass of Plugin"


def test_validate_key():
    with when:
        res = _validate_key("key")

    with then:
        assert res is True


@pytest.mark.parametrize("key", [
    None,  # not a string
    "invalid key",  # invalid identifier
    "pass",  # reserved keyword
])
def test_validate_key_invalid(key: str):
    with when, raises(Exception) as exc:
        _validate_key(key)

    with then:
        assert exc.type is ValueError
        assert str(exc.value) == (
            "`key` must be a valid Python identifier and not a reserved keyword"
        )


def test_validate_scenario():
    with given:
        class CustomScenario(Scenario):
            pass

    with when:
        res = _validate_scenario(CustomScenario)

    with then:
        assert res is True


def test_validate_scenario_invalid():
    with given:
        class CustomScenario:
            pass

    with when, raises(Exception) as exc:
        _validate_scenario(CustomScenario)

    with then:
        assert exc.type is TypeError
        assert str(exc.value) == "`scenario` must be a subclass of `Scenario`"
