from baby_steps import given, then, when
from pytest import raises

from vedro.core import Plugin
from vedro.core.di import ConflictError, Factory

from ._utils import BaseClass, DerivedClass, plugin

__all__ = ("plugin",)  # fixtures


def test_factory_register(*, plugin: Plugin):
    with given:
        factory = Factory[BaseClass](DerivedClass)

    with when:
        res = factory.register(lambda: DerivedClass(), plugin)

    with then:
        assert res is None


def test_factory_register_already_registered(*, plugin: Plugin):
    with given:
        factory = Factory[BaseClass](DerivedClass)
        factory.register(lambda: DerivedClass(), plugin)

    with when, raises(BaseException) as exc:
        factory.register(lambda: DerivedClass(), plugin)

    with then:
        assert exc.type is ConflictError


def test_factory_resolve():
    with given:
        factory = Factory[BaseClass](DerivedClass)

    with when:
        res = factory.resolve()

    with then:
        assert isinstance(res, DerivedClass)


def test_factory_call():
    with given:
        factory = Factory[BaseClass](DerivedClass)

    with when:
        res = factory()

    with then:
        assert isinstance(res, DerivedClass)


def test_factory_resolve_twice():
    with given:
        factory = Factory[BaseClass](DerivedClass)
        resolved = factory.resolve()

    with when:
        res = factory.resolve()

    with then:
        assert isinstance(res, DerivedClass)
        assert res != resolved


def test_factory_repr():
    with given:
        factory = Factory[BaseClass](DerivedClass)

    with when:
        res = repr(factory)

    with then:
        assert res == f"Factory({DerivedClass!r})"
