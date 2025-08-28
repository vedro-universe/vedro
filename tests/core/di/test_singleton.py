from baby_steps import given, then, when
from pytest import raises

from vedro.core import Plugin
from vedro.core.di import ConflictError, Singleton

from ._utils import BaseClass, DerivedClass, plugin

__all__ = ("plugin",)  # fixtures


def test_singleton_register(*, plugin: Plugin):
    with given:
        singleton = Singleton[BaseClass](DerivedClass)

    with when:
        res = singleton.register(lambda: DerivedClass(), plugin)

    with then:
        assert res is None


def test_singleton_register_already_registered(*, plugin: Plugin):
    with given:
        singleton = Singleton[BaseClass](DerivedClass)
        singleton.register(lambda: DerivedClass(), plugin)

    with when, raises(BaseException) as exc:
        singleton.register(lambda: DerivedClass(), plugin)

    with then:
        assert exc.type is ConflictError


def test_singleton_resolve():
    with given:
        singleton = Singleton[BaseClass](DerivedClass)

    with when:
        res = singleton.resolve()

    with then:
        assert isinstance(res, DerivedClass)


def test_singleton_call():
    with given:
        singleton = Singleton[BaseClass](DerivedClass)

    with when:
        res = singleton()

    with then:
        assert isinstance(res, DerivedClass)


def test_singleton_resolve_twice():
    with given:
        singleton = Singleton[BaseClass](DerivedClass)
        resolved = singleton.resolve()

    with when:
        res = singleton.resolve()

    with then:
        assert isinstance(res, DerivedClass)
        assert res == resolved


def test_singleton_repr():
    with given:
        singleton = Singleton[BaseClass](DerivedClass)

    with when:
        res = repr(singleton)

    with then:
        assert res == f"Singleton({DerivedClass!r})"
