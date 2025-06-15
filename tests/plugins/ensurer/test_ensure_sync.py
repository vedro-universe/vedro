from unittest.mock import Mock, call, patch, sentinel

from baby_steps import given, then, when
from pytest import raises

from vedro.plugins.ensurer import Ensure


def test_attempts_without_error():
    with given:
        ensure = Ensure(attempts=3)
        mock_ = Mock(side_effect=[sentinel.result])

    with when:
        res = ensure(mock_)(sentinel.arg, kwarg=sentinel.kwarg)

    with then:
        assert res is sentinel.result
        assert mock_.mock_calls == [
            call(sentinel.arg, kwarg=sentinel.kwarg)
        ]


def test_attempts_with_error():
    with given:
        ensure = Ensure(attempts=3)
        mock_ = Mock(side_effect=[Exception(), sentinel.result])

    with when:
        res = ensure(mock_)(sentinel.arg, kwarg=sentinel.kwarg)

    with then:
        assert res is sentinel.result
        assert mock_.mock_calls == [
            call(sentinel.arg, kwarg=sentinel.kwarg),
            call(sentinel.arg, kwarg=sentinel.kwarg)
        ]


def test_attempts_with_errors():
    with given:
        ensure = Ensure(attempts=3)
        mock_ = Mock(side_effect=[Exception(), Exception(), Exception()])

    with when, raises(Exception) as exc:
        ensure(mock_)(sentinel.arg, kwarg=sentinel.kwarg)

    with then:
        assert exc.type is Exception
        assert mock_.mock_calls == [
            call(sentinel.arg, kwarg=sentinel.kwarg),
            call(sentinel.arg, kwarg=sentinel.kwarg),
            call(sentinel.arg, kwarg=sentinel.kwarg)
        ]


def test_delay_without_error():
    with given:
        ensure = Ensure(attempts=3, delay=0.1)
        mock_ = Mock(side_effect=[sentinel.result])

    with when, patch("time.sleep") as sleep_:
        res = ensure(mock_)(sentinel.arg, kwarg=sentinel.kwarg)

    with then:
        assert res is sentinel.result
        assert mock_.mock_calls == [
            call(sentinel.arg, kwarg=sentinel.kwarg)
        ]
        assert sleep_.mock_calls == []


def test_delay_with_error():
    with given:
        ensure = Ensure(attempts=3, delay=0.1)
        mock_ = Mock(side_effect=[Exception(), sentinel.result])

    with when, patch("time.sleep") as sleep_:
        res = ensure(mock_)(sentinel.arg, kwarg=sentinel.kwarg)

    with then:
        assert res is sentinel.result
        assert mock_.mock_calls == [
            call(sentinel.arg, kwarg=sentinel.kwarg),
            call(sentinel.arg, kwarg=sentinel.kwarg)
        ]
        assert sleep_.mock_calls == [call(0.1)]


def test_delay_with_errors():
    with given:
        ensure = Ensure(attempts=3, delay=0.1)
        mock_ = Mock(side_effect=[Exception(), Exception(), Exception()])

    with when, patch("time.sleep") as sleep_, raises(BaseException) as exc:
        ensure(mock_)(sentinel.arg, kwarg=sentinel.kwarg)

    with then:
        assert exc.type is Exception
        assert mock_.mock_calls == [
            call(sentinel.arg, kwarg=sentinel.kwarg),
            call(sentinel.arg, kwarg=sentinel.kwarg),
            call(sentinel.arg, kwarg=sentinel.kwarg)
        ]
        assert sleep_.mock_calls == [call(0.1), call(0.1), call(0.1)]


def test_delay_fn_with_errors():
    with given:
        delay_ = Mock(side_effect=[0.1, 0.2, 0.3])
        ensure = Ensure(attempts=3, delay=delay_)

        mock_ = Mock(side_effect=[Exception(), Exception(), Exception()])

    with when, patch("time.sleep") as sleep_, raises(BaseException) as exc:
        ensure(mock_)(sentinel.arg, kwarg=sentinel.kwarg)

    with then:
        assert exc.type is Exception
        assert mock_.mock_calls == [
            call(sentinel.arg, kwarg=sentinel.kwarg),
            call(sentinel.arg, kwarg=sentinel.kwarg),
            call(sentinel.arg, kwarg=sentinel.kwarg)
        ]
        assert delay_.mock_calls == [call(1), call(2), call(3)]
        assert sleep_.mock_calls == [call(0.1), call(0.2), call(0.3)]


def test_swallow_exception():
    with given:
        ensure = Ensure(attempts=3, swallow=KeyError)
        mock_ = Mock(side_effect=[IndexError()])

    with when, raises(BaseException) as exc:
        ensure(mock_)(sentinel.arg, kwarg=sentinel.kwarg)

    with then:
        assert exc.type is IndexError
        assert mock_.mock_calls == [
            call(sentinel.arg, kwarg=sentinel.kwarg)
        ]


def test_swallow_exceptions():
    with given:
        ensure = Ensure(attempts=3, swallow=(KeyError, IndexError))
        mock_ = Mock(side_effect=[IndexError(), KeyError(), sentinel.result])

    with when:
        res = ensure(mock_)(sentinel.arg, kwarg=sentinel.kwarg)

    with then:
        assert res is sentinel.result
        assert mock_.mock_calls == [
            call(sentinel.arg, kwarg=sentinel.kwarg),
            call(sentinel.arg, kwarg=sentinel.kwarg),
            call(sentinel.arg, kwarg=sentinel.kwarg)
        ]


def test_logger_without_error():
    with given:
        logger_ = Mock()
        ensure = Ensure(attempts=3, logger=logger_)

        mock_ = Mock(side_effect=[sentinel.result])

    with when:
        res = ensure(mock_)(sentinel.arg, kwarg=sentinel.kwarg)

    with then:
        assert res is sentinel.result
        assert mock_.mock_calls == [
            call(sentinel.arg, kwarg=sentinel.kwarg)
        ]
        assert logger_.mock_calls == []


def test_logger_with_error():
    with given:
        logger_ = Mock()
        ensure = Ensure(attempts=3, logger=logger_)

        exception = Exception()
        mock_ = Mock(side_effect=[exception, sentinel.result])

    with when:
        res = ensure(mock_)(sentinel.arg, kwarg=sentinel.kwarg)

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


def test_logger_with_errors():
    with given:
        logger_ = Mock()
        ensure = Ensure(attempts=3, logger=logger_)

        exception = Exception()
        mock_ = Mock(side_effect=[exception, exception, exception])

    with when, raises(BaseException) as exc:
        ensure(mock_)(sentinel.arg, kwarg=sentinel.kwarg)

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


def test_repr():
    with given:
        ensure = Ensure(attempts=3, delay=0.1, swallow=ValueError)

    with when:
        res = repr(ensure)

    with then:
        assert res == "Ensure(attempts=3, delay=0.1, swallow=<class 'ValueError'>)"
