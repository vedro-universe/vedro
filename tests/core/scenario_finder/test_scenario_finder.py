from pytest import raises

from vedro._core._scenario_finder import ScenarioFinder


def test_scenario_finder():
    with raises(Exception) as exc_info:
        ScenarioFinder()

    assert exc_info.type is TypeError
    assert str(exc_info.value) == ("Can't instantiate abstract class ScenarioFinder "
                                   "with abstract methods find")
