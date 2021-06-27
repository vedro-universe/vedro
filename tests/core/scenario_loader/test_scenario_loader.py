from baby_steps import then, when
from pytest import raises

from vedro._core import ScenarioLoader


def test_scenario_loader():
    with when, raises(Exception) as exc_info:
        ScenarioLoader()

    with then:
        assert exc_info.type is TypeError
        assert "Can't instantiate abstract class ScenarioLoader" in str(exc_info.value)
