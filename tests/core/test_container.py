import pytest
from baby_steps import given, then, when
from pytest import raises

from vedro.core import Container, Factory, Plugin, PluginConfig, Singleton
from vedro.core._container import ConflictError


@pytest.fixture()
def plugin() -> Plugin:
    return Plugin(PluginConfig)


class BaseClass:
    pass


class DerivedClass(BaseClass):
    pass


def test_container_abc():
    with when, raises(BaseException) as exc:
        Container(None)

    with then:
        assert exc.type is TypeError


# Factory

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


# Singleton

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
