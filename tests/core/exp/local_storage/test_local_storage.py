from pathlib import Path

from baby_steps import given, then, when
from niltype import Nil
from pytest import raises

from vedro.core import Plugin
from vedro.core.exp.local_storage import LocalStorage, create_local_storage

from ._utils import local_storage, plugin

__all__ = ("plugin", "local_storage",)  # fixtures


async def test_put(*, local_storage: LocalStorage):
    with given:
        key, value = "<key>", "<value>"

    with when:
        res = await local_storage.put(key, value)

    with then:
        assert res is None


async def test_get(*, local_storage: LocalStorage):
    with given:
        key, value = "<key>", "<value>"
        await local_storage.put(key, value)

    with when:
        res = await local_storage.get(key)

    with then:
        assert res == value


async def test_get_nonexisting_key(*, local_storage: LocalStorage):
    with given:
        key = "<key>"

    with when:
        res = await local_storage.get(key)

    with then:
        assert res is Nil


async def test_get_without_flush(*, plugin: Plugin, tmp_path: Path):
    with given:
        key, value = "<key>", "<value>"

        local_storage1 = LocalStorage(plugin, project_dir=tmp_path)
        await local_storage1.put(key, value)

        local_storage2 = LocalStorage(plugin, project_dir=tmp_path)

    with when:
        res = await local_storage2.get(key)

    with then:
        assert res is Nil


async def test_get_with_flush(*, plugin: Plugin, tmp_path: Path):
    with given:
        key, value = "<key>", "<value>"

        local_storage1 = LocalStorage(plugin, project_dir=tmp_path)
        await local_storage1.put(key, value)
        await local_storage1.flush()

        local_storage2 = LocalStorage(plugin, project_dir=tmp_path)

    with when:
        res = await local_storage2.get(key)

    with then:
        assert res == value


async def test_flush_empty_storage(*, local_storage: LocalStorage):
    with when:
        res = await local_storage.flush()

    with then:
        assert res is None


async def test_flush(*, local_storage: LocalStorage):
    with given:
        key, value = "<key>", "<value>"
        await local_storage.put(key, value)

    with when:
        res = await local_storage.flush()

    with then:
        assert res is None


def test_create_local_storage(*, plugin: Plugin, tmp_path: Path):
    with when:
        res = create_local_storage(plugin, project_dir=tmp_path)

    with then:
        assert isinstance(res, LocalStorage)


def test_create_local_storage_incorrect_type(*, tmp_path: Path):
    with when, raises(BaseException) as exc:
        create_local_storage(None, project_dir=tmp_path)  # type: ignore

    with then:
        assert isinstance(exc.value, TypeError)
        assert str(exc.value) == "Expected Plugin instance, but got <class 'NoneType'>"
