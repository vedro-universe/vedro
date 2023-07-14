from typing import Callable

import pytest
from baby_steps import given, then, when

from vedro.core import AggregatedResult, MemoryArtifact, ScenarioResult

from ._utils import aggregated_result, make_scenario_result, make_step_result, make_vscenario

__all__ = ("aggregated_result",)  # fixtures


def test_inheritance(*, aggregated_result: AggregatedResult):
    with when:
        res = isinstance(aggregated_result, ScenarioResult)

    with then:
        assert res


def test_eq():
    with given:
        vscenario = make_vscenario()
        aggregated_result1 = AggregatedResult(vscenario)
        aggregated_result2 = AggregatedResult(vscenario)

    with when:
        is_eq = aggregated_result1 == aggregated_result2

    with then:
        assert is_eq


def test_not_eq():
    with given:
        vscenario = make_vscenario()
        aggregated_result = AggregatedResult(vscenario)
        scenario_result = ScenarioResult(vscenario)

    with when:
        is_eq = aggregated_result == scenario_result

    with then:
        assert not is_eq


def test_add_scenario_result(*, aggregated_result: AggregatedResult):
    with given:
        scenario_result = make_scenario_result()

    with when:
        res = aggregated_result.add_scenario_result(scenario_result)

    with then:
        assert res is None


def test_get_scenario_results(*, aggregated_result: AggregatedResult):
    with given:
        scenario_result1 = make_scenario_result()
        scenario_result2 = make_scenario_result()

        aggregated_result.add_scenario_result(scenario_result2)
        aggregated_result.add_scenario_result(scenario_result1)

    with when:
        scenario_results = aggregated_result.scenario_results

    with then:
        assert scenario_results == [scenario_result2, scenario_result1]


@pytest.mark.parametrize("get_scenario_result", [
    lambda: make_scenario_result(),
    lambda: make_scenario_result().mark_passed(),
    lambda: make_scenario_result().mark_failed(),
    lambda: make_scenario_result().mark_skipped(),
])
def test_from_existing_status_scope(get_scenario_result: Callable[[], ScenarioResult]):
    with given:
        scenario_result = get_scenario_result()
        scenario_result.set_scope({"key": "val"})

    with when:
        aggregated_result = AggregatedResult.from_existing(scenario_result, [scenario_result])

    with then:
        assert aggregated_result.status == scenario_result.status
        assert aggregated_result.started_at == scenario_result.started_at
        assert aggregated_result.ended_at == scenario_result.ended_at
        assert aggregated_result.scope == scenario_result.scope
        assert aggregated_result.artifacts == scenario_result.artifacts
        assert aggregated_result.step_results == scenario_result.step_results
        assert aggregated_result.extra_details == scenario_result.extra_details


@pytest.mark.parametrize("get_scenario_result", [
    lambda: make_scenario_result().set_started_at(1.0),
    lambda: make_scenario_result().set_ended_at(2.0),
])
def test_from_existing_started_ended(get_scenario_result: Callable[[], ScenarioResult]):
    with given:
        scenario_result = get_scenario_result()

    with when:
        aggregated_result = AggregatedResult.from_existing(scenario_result, [scenario_result])

    with then:
        assert aggregated_result.status == scenario_result.status
        assert aggregated_result.started_at == scenario_result.started_at
        assert aggregated_result.ended_at == scenario_result.ended_at
        assert aggregated_result.scope == scenario_result.scope
        assert aggregated_result.artifacts == scenario_result.artifacts
        assert aggregated_result.step_results == scenario_result.step_results
        assert aggregated_result.extra_details == scenario_result.extra_details


def test_from_existing_artifacts():
    with given:
        scenario_result = make_scenario_result()

        artifact1 = MemoryArtifact("name1", "text/plain", b"")
        scenario_result.attach(artifact1)

        artifact2 = MemoryArtifact("name2", "text/plain", b"")
        scenario_result.attach(artifact2)

    with when:
        aggregated_result = AggregatedResult.from_existing(scenario_result, [scenario_result])

    with then:
        assert aggregated_result.status == scenario_result.status
        assert aggregated_result.started_at == scenario_result.started_at
        assert aggregated_result.ended_at == scenario_result.ended_at
        assert aggregated_result.scope == scenario_result.scope
        assert aggregated_result.artifacts == scenario_result.artifacts
        assert aggregated_result.step_results == scenario_result.step_results
        assert aggregated_result.extra_details == scenario_result.extra_details


def test_from_existing_extra_details():
    with given:
        scenario_result = make_scenario_result()

        scenario_result.add_extra_details("<extra-detail-1>")
        scenario_result.add_extra_details("<extra-detail-2>")

    with when:
        aggregated_result = AggregatedResult.from_existing(scenario_result, [scenario_result])

    with then:
        assert aggregated_result.status == scenario_result.status
        assert aggregated_result.started_at == scenario_result.started_at
        assert aggregated_result.ended_at == scenario_result.ended_at
        assert aggregated_result.scope == scenario_result.scope
        assert aggregated_result.artifacts == scenario_result.artifacts
        assert aggregated_result.step_results == scenario_result.step_results
        assert aggregated_result.extra_details == scenario_result.extra_details


def test_from_existing_step_results():
    with given:
        scenario_result = make_scenario_result()

        step_result1 = make_step_result()
        scenario_result.add_step_result(step_result1)
        step_result2 = make_step_result()
        scenario_result.add_step_result(step_result2)

    with when:
        aggregated_result = AggregatedResult.from_existing(scenario_result, [scenario_result])

    with then:
        assert aggregated_result.status == scenario_result.status
        assert aggregated_result.started_at == scenario_result.started_at
        assert aggregated_result.ended_at == scenario_result.ended_at
        assert aggregated_result.scope == scenario_result.scope
        assert aggregated_result.artifacts == scenario_result.artifacts
        assert aggregated_result.step_results == scenario_result.step_results
        assert aggregated_result.extra_details == scenario_result.extra_details


def test_repr(*, aggregated_result: AggregatedResult):
    with given:
        vscenario = make_vscenario()
        aggregated_result = AggregatedResult(vscenario)

    with when:
        res = repr(aggregated_result)

    with then:
        assert res == f"<AggregatedResult {vscenario!r} {aggregated_result.status.value}>"
