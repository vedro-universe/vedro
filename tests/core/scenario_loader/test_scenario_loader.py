from baby_steps import then, when
from pytest import raises

from vedro.core import ScenarioLoader


def test_scenario_loader():
    with when, raises(BaseException) as exc:
        ScenarioLoader()

    with then:
        assert exc.type is TypeError
        assert "Can't instantiate abstract class ScenarioLoader" in str(exc.value)
