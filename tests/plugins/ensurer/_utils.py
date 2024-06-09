from typing import Any, Callable, Type, Union

import pytest

from vedro.core import Dispatcher, StepResult, VirtualStep
from vedro.events import StepFailedEvent, StepPassedEvent, StepRunEvent
from vedro.plugins.ensurer import Ensurer, EnsurerPlugin

__all__ = ("make_ensurer_plugin", "make_step_result", "run_step", "dispatcher", "ensurer", )


@pytest.fixture
def dispatcher():
    return Dispatcher()


@pytest.fixture
def ensurer(dispatcher: Dispatcher) -> EnsurerPlugin:
    return make_ensurer_plugin(dispatcher)


def make_ensurer_plugin(dispatcher: Dispatcher, *,
                        show_attempts: bool = Ensurer.show_attempts,
                        default_attempts: int = Ensurer.default_attempts,
                        default_delay: float = Ensurer.default_delay,
                        default_swallow: Type[Exception] = Ensurer.default_swallow
                        ) -> EnsurerPlugin:
    config = type("Ensurer", (Ensurer,), {
        "show_attempts": show_attempts,
        "default_attempts": default_attempts,
        "default_delay": default_delay,
        "default_swallow": default_swallow,
    })
    plugin = EnsurerPlugin(config)
    plugin.subscribe(dispatcher)
    return plugin


def make_step_result(step: Callable[..., Any]) -> StepResult:
    vstep = VirtualStep(step)
    return StepResult(vstep)


async def run_step(dispatcher: Dispatcher,
                   step_event: Type[Union[StepPassedEvent, StepFailedEvent]],
                   step_result: StepResult) -> None:
    await dispatcher.fire(StepRunEvent(step_result))
    step_result.step()
    await dispatcher.fire(step_event(step_result))
