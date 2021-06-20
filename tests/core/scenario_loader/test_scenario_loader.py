from pytest import raises

from vedro._core import ScenarioLoader


def test_scenario_loader():
    with raises(Exception) as exc_info:
        ScenarioLoader()

    assert exc_info.type is TypeError
    assert "Can't instantiate abstract class ScenarioLoader" in str(exc_info.value)
