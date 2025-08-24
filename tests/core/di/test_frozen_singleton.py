from baby_steps import given, then, when
from pytest import raises

from vedro.core import Plugin
from vedro.core.di import ConflictError, FrozenSingleton

from ._utils import BaseClass, DerivedClass, plugin

__all__ = ("plugin",)  # fixtures


def test_frozen_singleton_register(*, plugin: Plugin):
    with given:
        singleton = FrozenSingleton[BaseClass](DerivedClass)

    with when, raises(Exception) as exc:
        singleton.register(lambda: DerivedClass(), plugin)

    with then:
        assert exc.type is ConflictError
        assert str(exc.value) == (
            "Plugin(PluginConfig) is trying to register BaseClass, "
            "but this container is frozen and cannot be modified"
        )


def test_frozen_singleton_resolve():
    with given:
        singleton = FrozenSingleton[BaseClass](DerivedClass)

    with when:
        res = singleton.resolve()

    with then:
        assert isinstance(res, DerivedClass)


def test_frozen_singleton_call():
    with given:
        singleton = FrozenSingleton[BaseClass](DerivedClass)

    with when:
        res = singleton()

    with then:
        assert isinstance(res, DerivedClass)


def test_frozen_singleton_resolve_twice():
    with given:
        singleton = FrozenSingleton[BaseClass](DerivedClass)
        resolved = singleton.resolve()

    with when:
        res = singleton.resolve()

    with then:
        assert isinstance(res, DerivedClass)
        assert res == resolved


def test_frozen_singleton_repr():
    with given:
        singleton = FrozenSingleton[BaseClass](DerivedClass)

    with when:
        res = repr(singleton)

    with then:
        assert res == f"FrozenSingleton({DerivedClass!r})"
