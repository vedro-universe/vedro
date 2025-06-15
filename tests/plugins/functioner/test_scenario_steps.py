import pytest
from pytest import raises

from vedro.plugins.functioner import given, then, when
from vedro.plugins.functioner._scenario_steps import Given, Step, Then, When


@pytest.mark.parametrize("step", [given, when, then])
def test_step_context_manager(step: Step):
    with given as cm:
        assert cm is None


@pytest.mark.asyncio
@pytest.mark.parametrize("step", [given, when, then])
async def test_step_async_context_manager(step: Step):
    async with given as cm:
        assert cm is None


@pytest.mark.parametrize("step", [given, when, then])
def test_step_call(step: Step):
    step_ = step("step")

    with step_ as cm:
        assert cm is None
        assert step_._name == "step"

    assert step_._name is None


@pytest.mark.parametrize("step", [given, when, then])
def test_step_call_type_error(step: Step):
    with raises(BaseException) as exc:
        step(123)  # type: ignore[arg-type]

    assert exc.type is TypeError
    assert str(exc.value) == "Step name must be a string, got <class 'int'>"


@pytest.mark.parametrize("step", [Step(), Given(), When(), Then()])
def test_step_with_name_repr(step: Step):
    cls_name = step.__class__.__name__
    step_name = "<step>"

    res = repr(step(step_name))

    assert res == f"<{cls_name} name={step_name!r}>"


@pytest.mark.parametrize("step", [Step(), Given(), When(), Then()])
def test_step_repr_without_name(step: Step):
    cls_name = step.__class__.__name__

    res = repr(step)

    assert res == f"<{cls_name}>"
