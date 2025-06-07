from baby_steps import given, then, when
from pytest import raises

from vedro.plugins.ensurer._runtime_config import RuntimeConfig


def test_attempts():
    with given:
        runtime_config = RuntimeConfig()
        runtime_config.set_attempts(attempts := 3)

    with when:
        res = runtime_config.get_attempts()

    with then:
        assert res == attempts


def test_attempts_not_set():
    with given:
        runtime_config = RuntimeConfig()

    with when, raises(BaseException) as exc:
        runtime_config.get_attempts()

    with then:
        assert exc.type is ValueError
        assert str(exc.value) == "'attempts' is not set"


def test_delay():
    with given:
        runtime_config = RuntimeConfig()
        runtime_config.set_delay(delay := 1.0)

    with when:
        res = runtime_config.get_delay()

    with then:
        assert res == delay


def test_delay_not_set():
    with given:
        runtime_config = RuntimeConfig()

    with when, raises(BaseException) as exc:
        runtime_config.get_delay()

    with then:
        assert exc.type is ValueError
        assert str(exc.value) == "'delay' is not set"


def test_swallow():
    with given:
        runtime_config = RuntimeConfig()
        runtime_config.set_swallow(swallow := ValueError)

    with when:
        res = runtime_config.get_swallow()

    with then:
        assert res == swallow


def test_swallow_not_set():
    with given:
        runtime_config = RuntimeConfig()

    with when, raises(BaseException) as exc:
        runtime_config.get_swallow()

    with then:
        assert exc.type is ValueError
        assert str(exc.value) == "'swallow' is not set"


def test_logger():
    with given:
        runtime_config = RuntimeConfig()
        runtime_config.set_logger(logger := None)

    with when:
        res = runtime_config.get_logger()

    with then:
        assert res == logger


def test_logger_not_set():
    with given:
        runtime_config = RuntimeConfig()

    with when, raises(BaseException) as exc:
        runtime_config.get_logger()

    with then:
        assert exc.type is ValueError
        assert str(exc.value) == "'logger' is not set"
