from unittest.mock import patch

import pytest
from baby_steps import given, then, when

from vedro.core import Dispatcher, Report
from vedro.events import CleanupEvent
from vedro.plugins.tip_adviser import TipAdviser, TipAdviserPlugin

from ._utils import dispatcher, fire_arg_parsed_event, tip_adviser

__all__ = ("dispatcher", "tip_adviser",)  # fixtures


@pytest.mark.usefixtures(tip_adviser.__name__)
async def test_no_tips_with_default_args(*, dispatcher: Dispatcher):
    with given:
        await fire_arg_parsed_event(dispatcher)

        report = Report()
        cleanup_event = CleanupEvent(report)

    with when:
        await dispatcher.fire(cleanup_event)

    with then:
        assert report.summary == []


async def test_no_tips_when_plugin_disabled(*, dispatcher: Dispatcher):
    with given:
        class CustomTipAdviser(TipAdviser):
            show_tips = False

        tip_adviser = TipAdviserPlugin(CustomTipAdviser)
        tip_adviser.subscribe(dispatcher)

        await fire_arg_parsed_event(dispatcher, repeats=2)

        report = Report()
        cleanup_event = CleanupEvent(report)

    with when:
        await dispatcher.fire(cleanup_event)

    with then:
        assert report.summary == []


@pytest.mark.parametrize(("seq_idx", "tip"), [
    (0, "Tip: Consider using `--fixed-seed` for consistent results across repeated runs"),
    (1, "Tip: To disable these tips, run `vedro plugin disable vedro.plugins.tip_adviser`"),
])
@pytest.mark.usefixtures(tip_adviser.__name__)
async def test_random_tip_selection_with_repeats(seq_idx: int, tip: str, *,
                                                 dispatcher: Dispatcher):
    with given:
        await fire_arg_parsed_event(dispatcher, repeats=2)

        report = Report()
        cleanup_event = CleanupEvent(report)

    with when, patch("random.choice", lambda seq: seq[seq_idx]):
        await dispatcher.fire(cleanup_event)

    with then:
        assert report.summary == [tip]


@pytest.mark.parametrize(("seq_idx", "tip"), [
    (0, "Tip: Consider using `--fixed-seed` for consistent results across repeated runs"),
    (1, "Tip: Consider using `--fail-fast-on-repeat` to to stop after the first failing repeat"),
    (2, "Tip: To disable these tips, run `vedro plugin disable vedro.plugins.tip_adviser`"),
])
@pytest.mark.usefixtures(tip_adviser.__name__)
async def test_random_tip_selection_with_repeats_and_fail_fast(seq_idx: int, tip: str, *,
                                                               dispatcher: Dispatcher):
    with given:
        await fire_arg_parsed_event(dispatcher, repeats=2, fail_fast=True)

        report = Report()
        cleanup_event = CleanupEvent(report)

    with when, patch("random.choice", lambda seq: seq[seq_idx]):
        await dispatcher.fire(cleanup_event)

    with then:
        assert report.summary == [tip]
