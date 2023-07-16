import signal
import sys
from unittest.mock import Mock

if sys.version_info >= (3, 8):
    from signal import raise_signal
else:
    def raise_signal(sig: int) -> None:
        import os
        os.kill(os.getpid(), sig)

import pytest
from baby_steps import given, then, when
from pytest import raises

from vedro.core import Dispatcher
from vedro.core import MonotonicScenarioScheduler as Scheduler
from vedro.core import Report
from vedro.core.scenario_runner import Interrupted
from vedro.events import CleanupEvent, StartupEvent
from vedro.plugins.interrupter import InterrupterPluginTriggered

from ._utils import (
    HANDLE_SIGNAL,
    create_interrupter,
    dispatcher,
    fire_arg_parsed_event,
    interrupter,
    sig_handler_,
)

__all__ = ("dispatcher", "interrupter", "sig_handler_",)  # fixtures


@pytest.mark.asyncio
@pytest.mark.usefixtures(interrupter.__name__)
async def test_signal_handler(sig_handler_: Mock, dispatcher: Dispatcher):
    with given:
        await fire_arg_parsed_event(dispatcher)

        scheduler = Scheduler([])
        await dispatcher.fire(StartupEvent(scheduler))

    with when, raises(BaseException) as exc:
        raise_signal(HANDLE_SIGNAL)

    with then:
        assert exc.type is InterrupterPluginTriggered
        assert isinstance(exc.value, Interrupted)
        assert str(exc.value) == f"Stop after signal {HANDLE_SIGNAL!r} received"

        assert len(sig_handler_.mock_calls) == 0


@pytest.mark.asyncio
async def test_signal_handler_no_signals(sig_handler_: Mock, dispatcher: Dispatcher):
    with given:
        create_interrupter(dispatcher, signals=())

        await fire_arg_parsed_event(dispatcher)

        scheduler = Scheduler([])
        await dispatcher.fire(StartupEvent(scheduler))

    with when:
        raise_signal(HANDLE_SIGNAL)

    with then:
        assert "no exception"
        assert len(sig_handler_.mock_calls) == 1


@pytest.mark.asyncio
@pytest.mark.usefixtures(interrupter.__name__)
async def test_signal_handler_cleanup(sig_handler_: Mock, dispatcher: Dispatcher):
    with given:
        await fire_arg_parsed_event(dispatcher)

        scheduler = Scheduler([])
        await dispatcher.fire(StartupEvent(scheduler))

        event = CleanupEvent(Report())

    with when:
        await dispatcher.fire(event)

    with then:
        assert signal.getsignal(HANDLE_SIGNAL) == sig_handler_
