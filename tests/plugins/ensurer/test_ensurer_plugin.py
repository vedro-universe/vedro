from unittest.mock import Mock, call, patch

import pytest
from baby_steps import given, then, when
from pytest import raises

from vedro.core import Dispatcher
from vedro.events import StepPassedEvent
from vedro.plugins.ensurer import ensure

from ._utils import dispatcher, ensurer, make_ensurer_plugin, make_step_result, run_step

__all__ = ("dispatcher", "ensurer",)  # pytest fixtures


@pytest.mark.usefixtures(ensurer.__name__)
@pytest.mark.parametrize("step_event", [StepPassedEvent, StepPassedEvent])
async def test_without_exceptions(step_event, *, dispatcher: Dispatcher):
    with given:
        mock_ = Mock(side_effect=[None])
        step_result = make_step_result(ensure()(mock_))

    with when:
        await run_step(dispatcher, step_event, step_result)

    with then:
        assert step_result.extra_details == []


@pytest.mark.usefixtures(ensurer.__name__)
@pytest.mark.parametrize("step_event", [StepPassedEvent, StepPassedEvent])
async def test_with_exceptions(step_event, *, dispatcher: Dispatcher):
    with given:
        mock_ = Mock(side_effect=[Exception(), None])
        step_result = make_step_result(ensure()(mock_))

    with when:
        await run_step(dispatcher, step_event, step_result)

    with then:
        assert step_result.extra_details == [
            "[1] attempt failed with Exception()",
            "[2] attempt succeeded",
        ]


@pytest.mark.usefixtures(ensurer.__name__)
@pytest.mark.parametrize("step_event", [StepPassedEvent, StepPassedEvent])
async def test_with_exceptions_outside_step(step_event, *, dispatcher: Dispatcher):
    with given:
        mock_ = Mock(side_effect=[Exception(), None])
        step_result = make_step_result(lambda: ensure()(mock_)())

    with when:
        await run_step(dispatcher, step_event, step_result)

    with then:
        assert step_result.extra_details == []


async def test_show_attempts_disabled(*, dispatcher: Dispatcher):
    with given:
        make_ensurer_plugin(dispatcher, show_attempts=False)

        mock_ = Mock(side_effect=[Exception(), None])
        step_result = make_step_result(ensure()(mock_))

    with when:
        await run_step(dispatcher, StepPassedEvent, step_result)

    with then:
        assert step_result.extra_details == []


async def test_custom_attempts(*, dispatcher: Dispatcher):
    with given:
        make_ensurer_plugin(dispatcher, default_attempts=1)

        mock_ = Mock(side_effect=[Exception(), None])
        step_result = make_step_result(ensure()(mock_))

    with when, raises(BaseException) as exc:
        await run_step(dispatcher, StepPassedEvent, step_result)

    with then:
        assert exc.type is Exception
        assert len(mock_.mock_calls) == 1


async def test_custom_delay(*, dispatcher: Dispatcher):
    with given:
        make_ensurer_plugin(dispatcher, default_delay=0.1)

        mock_ = Mock(side_effect=[Exception(), None])
        step_result = make_step_result(ensure()(mock_))

    with when, patch("time.sleep") as sleep_:
        await run_step(dispatcher, StepPassedEvent, step_result)

    with then:
        assert len(mock_.mock_calls) == 2
        assert sleep_.mock_calls == [call(0.1)]


async def test_custom_swallow(*, dispatcher: Dispatcher):
    with given:
        make_ensurer_plugin(dispatcher, default_swallow=ZeroDivisionError)

        mock_ = Mock(side_effect=[Exception(), None])
        step_result = make_step_result(ensure()(mock_))

    with when, raises(BaseException) as exc:
        await run_step(dispatcher, StepPassedEvent, step_result)

    with then:
        assert exc.type is Exception
        assert len(mock_.mock_calls) == 1
