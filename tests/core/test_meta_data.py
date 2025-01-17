from baby_steps import given, then, when
from niltype import Nil
from pytest import raises

from vedro.core._meta_data import MetaData


def test_set():
    with given:
        data = MetaData()

    with when:
        res = data._set("key", "value")

    with then:
        assert res is None


def test_get():
    with given:
        data = MetaData()
        data._set("key", "value")

    with when:
        res = data.get("key")

    with then:
        assert res == "value"


def test_get_non_existing_key():
    with given:
        data = MetaData()

    with when:
        res = data.get("non_existing_key")

    with then:
        assert res is Nil


def test_has_existing_key():
    with given:
        data = MetaData()
        data._set("key", "value")

    with when:
        res = data.has("key")

    with then:
        assert res is True


def test_has_non_existing_key():
    with given:
        data = MetaData()

    with when:
        res = data.has("non_existing_key")

    with then:
        assert res is False


def test_items_empty():
    with given:
        data = MetaData()

    with when:
        res = data.items()

    with then:
        assert list(res) == []


def test_items_with_data():
    with given:
        initial_data = {"key1": "value1", "key2": "value2"}
        data = MetaData(initial_data)

    with when:
        res = data.items()

    with then:
        assert set(res) == set(initial_data.items())


def test_repr_empty():
    with given:
        data = MetaData()

    with when:
        representation = repr(data)

    with then:
        assert representation == "MetaData({})"


def test_repr_with_data():
    with given:
        initial_data = {"key": "value", "another_key": True}
        data = MetaData(initial_data)

    with when:
        representation = repr(data)

    with then:
        assert representation == f"MetaData({initial_data!r})"


def test_initialization_with_data():
    with given:
        initial_data = {"key": "value"}

    with when:
        data = MetaData(initial_data)

    with then:
        assert data.get("key") == "value"


def test_set_overwrites_existing_key():
    with given:
        data = MetaData({"key": "initial"})

    with when:
        data._set("key", "updated")
        result = data.get("key")

    with then:
        assert result == "updated"


def test_items_immutable():
    with given:
        data = MetaData({"key": "value"})
        items_view = data.items()

    with when, raises(Exception) as exc:
        items_view["key"] = "updated"

    with then:
        assert exc.type is TypeError
