from os import linesep

from baby_steps import given, then, when
from pytest import raises

from vedro.commands.run_command._plugin_config_validator import PluginConfigValidator
from vedro.core import Plugin, PluginConfig

from ._utils import tmp_dir

__all__ = ("tmp_dir",)  # fixtures


class CustomPlugin(Plugin):
    pass


class CustomPluginConfig(PluginConfig):
    plugin = CustomPlugin


def test_validate():
    with given:
        class CustomPluginConfigWithDependency(PluginConfig):
            plugin = CustomPlugin
            depends_on = [CustomPluginConfig]

        validator = PluginConfigValidator()

    with when:
        res = validator.validate(CustomPluginConfigWithDependency, {CustomPluginConfig})

    with then:
        assert res is None


def test_validate_not_subclass():
    with given:
        validator = PluginConfigValidator()

    with when, raises(BaseException) as exc:
        validator.validate(object, set())

    with then:
        assert exc.type is TypeError
        assert str(exc.value) == (
            "PluginConfig '<class 'object'>' must be a subclass of 'vedro.core.PluginConfig'"
        )


def test_validate_not_subclass_plugin():
    with given:
        class InvalidPluginConfig(PluginConfig):
            plugin = object

        validator = PluginConfigValidator()

    with when, raises(BaseException) as exc:
        validator.validate(InvalidPluginConfig, set())

    with then:
        assert exc.type is TypeError
        assert str(exc.value) == (
            "Attribute 'plugin' in 'InvalidPluginConfig' must be a subclass of 'vedro.core.Plugin'"
        )


def test_validate_depends_on_not_sequence():
    with given:
        class InvalidPluginConfig(PluginConfig):
            plugin = CustomPlugin
            depends_on = object()

        validator = PluginConfigValidator()

    with when, raises(BaseException) as exc:
        validator.validate(InvalidPluginConfig, set())

    with then:
        assert exc.type is TypeError
        assert str(exc.value) == (
            "Attribute 'depends_on' in 'InvalidPluginConfig' plugin must be a list or "
            "another sequence type (<class 'object'> provided). " +
            linesep.join([
                "Example:",
                "  @computed",
                "  def depends_on(cls):",
                "    return [Config.Plugins.Tagger]"
            ])
        )


def test_validate_depends_on_not_subclass():
    with given:
        class InvalidPluginConfig(PluginConfig):
            plugin = CustomPlugin
            depends_on = [object]

        validator = PluginConfigValidator()

    with when, raises(BaseException) as exc:
        validator.validate(InvalidPluginConfig, set())

    with then:
        assert exc.type is TypeError
        assert str(exc.value) == (
            "Dependency '<class 'object'>' in 'depends_on' of 'InvalidPluginConfig' "
            "must be a subclass of 'vedro.core.PluginConfig'"
        )


def test_validate_depends_on_not_found():
    with given:
        class InvalidPluginConfig(PluginConfig):
            plugin = CustomPlugin
            depends_on = [CustomPluginConfig]

        validator = PluginConfigValidator()

    with when, raises(BaseException) as exc:
        validator.validate(InvalidPluginConfig, set())

    with then:
        assert exc.type is ValueError
        assert str(exc.value) == (
            "Dependency 'CustomPluginConfig' in 'depends_on' of 'InvalidPluginConfig' "
            "is not found among the configured plugins"
        )


def test_validate_depends_on_not_enabled():
    with given:
        class DisabledPluginConfig(PluginConfig):
            plugin = CustomPlugin
            enabled = False

        class InvalidPluginConfig(PluginConfig):
            plugin = CustomPlugin
            depends_on = [DisabledPluginConfig]

        validator = PluginConfigValidator()

    with when, raises(BaseException) as exc:
        validator.validate(InvalidPluginConfig, {DisabledPluginConfig})

    with then:
        assert exc.type is ValueError
        assert str(exc.value) == (
            "Dependency 'DisabledPluginConfig' in 'depends_on' of 'InvalidPluginConfig' "
            "is not enabled"
        )


def test_validate_unknown_attributes():
    with given:
        class InvalidPluginConfig(PluginConfig):
            plugin = CustomPlugin
            unknown = "unknown"

        validator = PluginConfigValidator()

    with when, raises(BaseException) as exc:
        validator.validate(InvalidPluginConfig, set())

    with then:
        assert exc.type is AttributeError
        assert str(exc.value) == (
            "InvalidPluginConfig configuration contains unknown attributes: unknown"
        )


def test_validate_unknown_attributes_disabled():
    with given:
        class InvalidPluginConfig(PluginConfig):
            plugin = CustomPlugin
            unknown = "unknown"

        validator = PluginConfigValidator(validate_plugins_attrs=False)

    with when:
        validator.validate(InvalidPluginConfig, set())

    with then:
        # no exception raised
        pass
