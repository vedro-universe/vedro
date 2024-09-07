import pytest
from baby_steps import given, then, when
from pytest import raises

from vedro.plugins.slicer import BaseSlicingStrategy, RoundRobinSlicingStrategy

from ._utils import make_vscenario


def test_base_slicing_strategy_abstract():
    with when, raises(BaseException) as exc_info:
        BaseSlicingStrategy(total=2, index=0)

    with then:
        assert exc_info.type is TypeError


@pytest.mark.parametrize(("total", "index", "current_index", "expected"), [
    (2, 0, 0, True),    # Should run, as current_index % total == index
    (2, 0, 1, False),   # Should not run, as 1 % 2 != 0
    (2, 1, 1, True),    # Should run, as current_index % total == index
    (3, 1, 4, True),    # Should run, as 4 % 3 == 1
])
def test_round_robin_slicing_strategy(total, index, current_index, expected):
    with given:
        strategy = RoundRobinSlicingStrategy(total, index)

    with when:
        result = strategy.should_run(make_vscenario(), current_index)

    with then:
        assert result == expected
