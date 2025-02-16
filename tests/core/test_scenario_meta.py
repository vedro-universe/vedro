import pytest
from baby_steps import given, then, when
from niltype import Nil
from pytest import raises

from vedro import Scenario
from vedro.core import Plugin, PluginConfig, get_scenario_meta, set_scenario_meta
from vedro.core._scenario_meta import (
    _get_meta_key,
    _get_plugin_name,
    _validate_key,
    _validate_plugin,
    _validate_scenario,
)


class CustomPlugin(Plugin):
    pass


def test_get_plugin_class_name():
    with when:
        name = _get_plugin_name(CustomPlugin)

    with then:
        assert name == f"{CustomPlugin.__module__}.{CustomPlugin.__name__}"


def test_get_plugin_instance_name():
    with when:
        name = _get_plugin_name(CustomPlugin(PluginConfig))

    with then:
        assert name == f"{CustomPlugin.__module__}.{CustomPlugin.__name__}"


def test_get_meta_key():
    with given:
        namespace = _get_plugin_name(CustomPlugin)

    with when:
        key = _get_meta_key(CustomPlugin, "key")

    with then:
        assert key == f"{namespace}.key"


def test_validate_plugin_class():
    with when:
        res = _validate_plugin(CustomPlugin)

    with then:
        assert res is True


def test_validate_plugin_instance():
    with when:
        res = _validate_plugin(CustomPlugin(PluginConfig))

    with then:
        assert res is True


def test_validate_plugin_invalid():
    with given:
        class CustomPluginInvalid:
            pass

    with when, raises(Exception) as exc:
        _validate_plugin(CustomPluginInvalid)

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
        class CustomScenarioInvalid:
            pass

    with when, raises(Exception) as exc:
        _validate_scenario(CustomScenarioInvalid)

    with then:
        assert exc.type is TypeError
        assert str(exc.value) == "`scenario` must be a subclass of `Scenario`"


def test_set_scenario_meta():
    with given:
        class CustomScenario(Scenario):
            pass

        key, value = "key", "value"

    with when:
        set_scenario_meta(CustomScenario, key, value, plugin=CustomPlugin)

    with then:
        assert get_scenario_meta(CustomScenario, key, plugin=CustomPlugin) == value


def test_set_scenario_meta_fallback():
    with given:
        class CustomScenario(Scenario):
            pass

        key, value = "key", "value"
        fallback_key = "__vedro__key__"

    with when:
        set_scenario_meta(CustomScenario, key, value,
                          plugin=CustomPlugin, fallback_key=fallback_key)

    with then:
        assert getattr(CustomScenario, fallback_key) == value


def test_get_scenario_meta_fallback():
    with given:
        class CustomScenario(Scenario):
            pass

        key, value = "key", "value"
        fallback_key = "__vedro__key__"

        setattr(CustomScenario, fallback_key, value)

    with when:
        res = get_scenario_meta(CustomScenario, key,
                                plugin=CustomPlugin, fallback_key=fallback_key)

    with then:
        assert res == value


def test_get_scenario_meta_non_existing_key():
    with given:
        class CustomScenario(Scenario):
            pass

    with when:
        res = get_scenario_meta(CustomScenario, "non_existing_key", plugin=CustomPlugin)

    with then:
        assert res is Nil


def test_get_scenario_meta_default():
    with given:
        class CustomScenario(Scenario):
            pass

    with when:
        res = get_scenario_meta(CustomScenario, "key", plugin=CustomPlugin, default="default")

    with then:
        assert res == "default"


def test_get_scenario_meta_template():
    with given:
        class CustomScenarioTemplate(Scenario):
            pass

        key, value = "key", "template_value"
        set_scenario_meta(CustomScenarioTemplate, key, value, plugin=CustomPlugin)

        class CustomScenario(Scenario):
            __vedro__template__ = CustomScenarioTemplate

    with when:
        res = get_scenario_meta(CustomScenario, key, plugin=CustomPlugin)

    with then:
        assert res == value
