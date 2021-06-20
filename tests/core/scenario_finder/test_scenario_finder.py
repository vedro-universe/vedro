from pytest import raises

from vedro._core import ScenarioFinder


def test_scenario_finder():
    with raises(Exception) as exc_info:
        ScenarioFinder()

    assert exc_info.type is TypeError
    assert "Can't instantiate abstract class ScenarioFinder" in str(exc_info.value)
