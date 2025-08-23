from baby_steps import then, when
from pytest import raises

from vedro.core.di import Container


def test_container_abc():
    with when, raises(BaseException) as exc:
        Container(None)

    with then:
        assert exc.type is TypeError
