import pytest
from baby_steps import given, then, when
from pytest import raises

from vedro import effect


def test_effect_sync_function_returning_true():
    with given:
        @effect
        def my_effect():
            return True

    with when:
        result = my_effect()

    with then:
        assert result is True
        assert hasattr(my_effect, "__vedro__effect__")
        assert my_effect.__vedro__effect__ is True


def test_effect_sync_function_returning_none():
    with given:
        @effect
        def my_effect():
            return None

    with when:
        result = my_effect()

    with then:
        assert result is True  # None should be converted to True
        assert hasattr(my_effect, "__vedro__effect__")
        assert my_effect.__vedro__effect__ is True


def test_effect_sync_function_with_no_return():
    with given:
        @effect
        def my_effect():
            pass  # Implicit None return

    with when:
        result = my_effect()

    with then:
        assert result is True


@pytest.mark.parametrize("return_value", [
    False,
    42,
    "string",
    [],
    {},
])
def test_effect_sync_function_returning_false(return_value):
    with given:
        @effect
        def my_effect():
            return return_value

    with when, raises(BaseException) as exc:
        my_effect()

    with then:
        assert exc.type is TypeError
        assert str(exc.value) == (
            "Effect 'my_effect' must return True (type: bool), "
            f"got {return_value!r} (type: {type(return_value).__name__})"
        )


@pytest.mark.asyncio
async def test_effect_async_function_returning_true():
    with given:
        @effect
        async def my_effect():
            return True

    with when:
        result = await my_effect()

    with then:
        assert result is True
        assert hasattr(my_effect, "__vedro__effect__")
        assert my_effect.__vedro__effect__ is True


@pytest.mark.asyncio
async def test_effect_async_function_returning_none():
    with given:
        @effect
        async def my_effect():
            return None

    with when:
        result = await my_effect()

    with then:
        assert result is True  # None should be converted to True
        assert hasattr(my_effect, "__vedro__effect__")
        assert my_effect.__vedro__effect__ is True


@pytest.mark.asyncio
async def test_effect_async_function_with_no_return():
    with given:
        @effect
        async def my_effect():
            pass  # Implicit None return

    with when:
        result = await my_effect()

    with then:
        assert result is True


@pytest.mark.parametrize("return_value", [
    False,
    42,
    "string",
    [],
    {},
])
async def test_effect_async_function_returning_false(return_value):
    with given:
        @effect
        async def my_effect():
            return return_value

    with when, raises(BaseException) as exc:
        await my_effect()

    with then:
        assert exc.type is TypeError
        assert str(exc.value) == (
            "Effect 'my_effect' must return True (type: bool), "
            f"got {return_value!r} (type: {type(return_value).__name__})"
        )
