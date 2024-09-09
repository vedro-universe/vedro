import pytest
from baby_steps import given, then, when
from pytest import raises

from vedro.plugins.slicer import (
    BaseSlicingStrategy,
    RoundRobinSlicingStrategy,
    SkipAdjustedSlicingStrategy,
)

from ._utils import make_vscenario


def test_base_slicing_strategy_abstract():
    with when, raises(BaseException) as exc_info:
        BaseSlicingStrategy(total=2, index=0)

    with then:
        assert exc_info.type is TypeError


@pytest.mark.parametrize(("total", "index", "current_index", "expected"), [
    (2, 0, 0, True),    # Should run, as current_index % total == index
    (2, 0, 1, False),   # Should not run, as 1 % 2 != 0
    (2, 0, 2, True),    # Should run, as 2 % 2 == 0
    (2, 1, 0, False),   # Should not run, as 0 % 2 != 1
    (2, 1, 1, True),    # Should run, as 1 % 2 == 1
    (2, 1, 2, False),   # Should not run, as 2 % 2 != 1
])
def test_round_robin_slicing_strategy(total, index, current_index, expected):
    with given:
        strategy = RoundRobinSlicingStrategy(total, index)

    with when:
        result = strategy.should_run(make_vscenario(), current_index)

    with then:
        assert result == expected


@pytest.mark.parametrize(("index", "expected"), [
    (0, [True, False, False, True]),  # Worker 0 runs the first and fourth
    (1, [False, True, False, False]),  # Worker 1 runs the second
    (2, [False, False, True, False]),  # Worker 2 runs the third
])
def test_skip_adjusted_slicing_no_skipped(index, expected):
    with given:
        total = 3
        strategy = SkipAdjustedSlicingStrategy(total=total, index=index)
        scenario_skips = [False, False, False, False]

    with when:
        results = [strategy.should_run(make_vscenario(is_skipped=skipped), idx)
                   for idx, skipped in enumerate(scenario_skips)]

    with then:
        assert results == expected


@pytest.mark.parametrize(("index", "expected"), [
    (0, [False, False, True, True]),  # Worker 0 runs the third and fourth
    (1, [False, True, False, False]),  # Worker 1 runs the second
    (2, [True, False, False, False]),  # Worker 2 runs the first
])
def test_skip_adjusted_slicing_multiple_skipped(index, expected):
    with given:
        strategy = SkipAdjustedSlicingStrategy(total=3, index=index)
        scenario_skips = [True, True, False, True]

    with when:
        results = [strategy.should_run(make_vscenario(is_skipped=skipped), idx)
                   for idx, skipped in enumerate(scenario_skips)]

    with then:
        assert results == expected
