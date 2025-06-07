from pytest import raises

from vedro.core import ScenarioFinder


def test_scenario_finder():
    with raises(BaseException) as exc:
        ScenarioFinder()

    assert exc.type is TypeError
    assert "Can't instantiate abstract class ScenarioFinder" in str(exc.value)
