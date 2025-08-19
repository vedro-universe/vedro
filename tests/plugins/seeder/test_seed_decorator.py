from pathlib import Path

import pytest
from baby_steps import given, then, when

from vedro import Scenario
from vedro.core import Dispatcher, get_scenario_meta
from vedro.plugins.seeder import SeederPlugin, seed

from ._utils import dispatcher, seeder

__all__ = ("dispatcher", "seeder")  # fixtures


CUSTOM_SEED = "custom-seed"


async def test_seed_decorator_on_scenario_class(*, dispatcher: Dispatcher):
    with given:
        @seed(CUSTOM_SEED)
        class CustomScenario(Scenario):
            __file__ = Path("custom_scenario.py").absolute()

    with when:
        seed_value = get_scenario_meta(CustomScenario, key="seed", plugin=SeederPlugin)

    with then:
        assert seed_value == CUSTOM_SEED


async def test_seed_decorator_type_error():
    with when, pytest.raises(Exception) as exc_info:
        @seed(CUSTOM_SEED)
        class Scenario:
            pass

    with then:
        assert exc_info.type is TypeError
        assert "Decorator @seed can be used only with Vedro scenarios" in str(exc_info.value)
        assert f"@seed({CUSTOM_SEED!r})" in str(exc_info.value)


async def test_seed_decorator_on_function():
    with given:
        def fn():
            pass

    with when, pytest.raises(Exception) as exc_info:
        seed(CUSTOM_SEED)(fn)

    with then:
        assert exc_info.type is TypeError
        assert "Decorator @seed can be used only with Vedro scenarios" in str(exc_info.value)
        assert f"@seed({CUSTOM_SEED!r})" in str(exc_info.value)
