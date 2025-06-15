from unittest.mock import AsyncMock, Mock, call, patch, sentinel

from baby_steps import given, then, when
from pytest import raises

from vedro.plugins.ensurer import Ensure


async def test_attempts_without_error():
    with given:
        ensure = Ensure(attempts=3)
        mock_ = AsyncMock(side_effect=[sentinel.result])

    with when:
        res = await ensure(mock_)(sentinel.arg, kwarg=sentinel.kwarg)

    with then:
        assert res is sentinel.result
        assert mock_.mock_calls == [
            call(sentinel.arg, kwarg=sentinel.kwarg)
        ]


async def test_attempts_with_error():
    with given:
        ensure = Ensure(attempts=3)
        mock_ = AsyncMock(side_effect=[Exception(), sentinel.result])

    with when:
        res = await ensure(mock_)(sentinel.arg, kwarg=sentinel.kwarg)

    with then:
        assert res is sentinel.result
        assert mock_.mock_calls == [
            call(sentinel.arg, kwarg=sentinel.kwarg),
            call(sentinel.arg, kwarg=sentinel.kwarg)
        ]


async def test_attempts_with_errors():
    with given:
        ensure = Ensure(attempts=3)
        mock_ = AsyncMock(side_effect=[Exception(), Exception(), Exception()])

    with when, raises(BaseException) as exc:
        await ensure(mock_)(sentinel.arg, kwarg=sentinel.kwarg)

    with then:
        assert exc.type is Exception
        assert mock_.mock_calls == [
            call(sentinel.arg, kwarg=sentinel.kwarg),
            call(sentinel.arg, kwarg=sentinel.kwarg),
            call(sentinel.arg, kwarg=sentinel.kwarg)
        ]


async def test_delay_without_error():
    with given:
        ensure = Ensure(attempts=3, delay=0.1)
        mock_ = AsyncMock(side_effect=[sentinel.result])

    with when, patch("asyncio.sleep") as sleep_:
        res = await ensure(mock_)(sentinel.arg, kwarg=sentinel.kwarg)

    with then:
        assert res is sentinel.result
        assert mock_.mock_calls == [
            call(sentinel.arg, kwarg=sentinel.kwarg)
        ]
        assert sleep_.mock_calls == []


async def test_delay_with_error():
    with given:
        ensure = Ensure(attempts=3, delay=0.1)
        mock_ = AsyncMock(side_effect=[Exception(), sentinel.result])

    with when, patch("asyncio.sleep") as sleep_:
        res = await ensure(mock_)(sentinel.arg, kwarg=sentinel.kwarg)

    with then:
        assert res is sentinel.result
        assert mock_.mock_calls == [
            call(sentinel.arg, kwarg=sentinel.kwarg),
            call(sentinel.arg, kwarg=sentinel.kwarg)
        ]
        assert sleep_.mock_calls == [call(0.1)]


async def test_delay_with_errors():
    with given:
        ensure = Ensure(attempts=3, delay=0.1)
        mock_ = AsyncMock(side_effect=[Exception(), Exception(), Exception()])

    with when, patch("asyncio.sleep") as sleep_, raises(BaseException) as exc:
        await ensure(mock_)(sentinel.arg, kwarg=sentinel.kwarg)

    with then:
        assert exc.type is Exception
        assert mock_.mock_calls == [
            call(sentinel.arg, kwarg=sentinel.kwarg),
            call(sentinel.arg, kwarg=sentinel.kwarg),
            call(sentinel.arg, kwarg=sentinel.kwarg)
        ]
        assert sleep_.mock_calls == [call(0.1), call(0.1), call(0.1)]


async def test_delay_fn_with_errors():
    with given:
        delay_ = Mock(side_effect=[0.1, 0.2, 0.3])
        ensure = Ensure(attempts=3, delay=delay_)

        mock_ = AsyncMock(side_effect=[Exception(), Exception(), Exception()])

    with when, patch("asyncio.sleep") as sleep_, raises(BaseException) as exc:
        await ensure(mock_)(sentinel.arg, kwarg=sentinel.kwarg)

    with then:
        assert exc.type is Exception
        assert mock_.mock_calls == [
            call(sentinel.arg, kwarg=sentinel.kwarg),
            call(sentinel.arg, kwarg=sentinel.kwarg),
            call(sentinel.arg, kwarg=sentinel.kwarg)
        ]
        assert delay_.mock_calls == [call(1), call(2), call(3)]
        assert sleep_.mock_calls == [call(0.1), call(0.2), call(0.3)]


async def test_swallow_exception():
    with given:
        ensure = Ensure(attempts=3, swallow=KeyError)
        mock_ = AsyncMock(side_effect=[IndexError()])

    with when, raises(BaseException) as exc:
        await ensure(mock_)(sentinel.arg, kwarg=sentinel.kwarg)

    with then:
        assert exc.type is IndexError
        assert mock_.mock_calls == [
            call(sentinel.arg, kwarg=sentinel.kwarg)
        ]


async def test_swallow_exceptions():
    with given:
        ensure = Ensure(attempts=3, swallow=(KeyError, IndexError))
        mock_ = AsyncMock(side_effect=[IndexError(), KeyError(), sentinel.result])

    with when:
        res = await ensure(mock_)(sentinel.arg, kwarg=sentinel.kwarg)

    with then:
        assert res is sentinel.result
        assert mock_.mock_calls == [
            call(sentinel.arg, kwarg=sentinel.kwarg),
            call(sentinel.arg, kwarg=sentinel.kwarg),
            call(sentinel.arg, kwarg=sentinel.kwarg)
        ]


async def test_logger_without_error():
    with given:
        logger_ = Mock()
        ensure = Ensure(attempts=3, logger=logger_)

        mock_ = AsyncMock(side_effect=[sentinel.result])

    with when:
        res = await ensure(mock_)(sentinel.arg, kwarg=sentinel.kwarg)

    with then:
        assert res is sentinel.result
        assert mock_.mock_calls == [
            call(sentinel.arg, kwarg=sentinel.kwarg)
        ]
        assert logger_.mock_calls == []


async def test_logger_with_error():
    with given:
        logger_ = Mock()
        ensure = Ensure(attempts=3, logger=logger_)

        exception = Exception()
        mock_ = AsyncMock(side_effect=[exception, sentinel.result])

    with when:
        res = await ensure(mock_)(sentinel.arg, kwarg=sentinel.kwarg)

    with then:
        assert res is sentinel.result
        assert mock_.mock_calls == [
            call(sentinel.arg, kwarg=sentinel.kwarg),
            call(sentinel.arg, kwarg=sentinel.kwarg)
        ]
        assert logger_.mock_calls == [
            call(mock_, 1, exception),
            call(mock_, 2, None)
        ]


async def test_logger_with_errors():
    with given:
        logger_ = Mock()
        ensure = Ensure(attempts=3, logger=logger_)

        exception = Exception()
        mock_ = AsyncMock(side_effect=[exception, exception, exception])

    with when, raises(BaseException) as exc:
        await ensure(mock_)(sentinel.arg, kwarg=sentinel.kwarg)

    with then:
        assert exc.type is Exception
        assert mock_.mock_calls == [
            call(sentinel.arg, kwarg=sentinel.kwarg),
            call(sentinel.arg, kwarg=sentinel.kwarg),
            call(sentinel.arg, kwarg=sentinel.kwarg)
        ]
        assert logger_.mock_calls == [
            call(mock_, 1, exception),
            call(mock_, 2, exception),
            call(mock_, 3, exception)
        ]
