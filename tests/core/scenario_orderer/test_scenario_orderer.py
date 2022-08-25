from baby_steps import then, when
from pytest import raises

from vedro.core import ScenarioOrderer


def test_abc():
    with when, raises(BaseException) as exc_info:
        ScenarioOrderer()

    with then:
        assert exc_info.type is TypeError
        assert "Can't instantiate abstract class ScenarioOrderer" in str(exc_info.value)
