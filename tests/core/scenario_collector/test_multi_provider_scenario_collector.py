from pathlib import Path
from time import monotonic_ns
from typing import List, Optional
from unittest.mock import Mock, call

from pytest import raises

from vedro import Scenario, given, then, when
from vedro.core import ModuleLoader, Plugin, VirtualScenario
from vedro.core.scenario_collector import (
    MultiProviderScenarioCollector,
    ScenarioProvider,
    ScenarioSource,
)

from ._utils import loaded_module, module_loader, tmp_dir

__all__ = ("tmp_dir", "loaded_module", "module_loader",)  # fixtures


def make_vscenario() -> VirtualScenario:
    class _Scenario(Scenario):
        __file__ = Path(f"scenario_{monotonic_ns()}.py").absolute()

    return VirtualScenario(_Scenario, steps=[])


def make_provider(scenarios: List[VirtualScenario],
                  spy: Optional[Mock] = None) -> ScenarioProvider:
    class Provider(ScenarioProvider):
        async def provide(self, source: ScenarioSource) -> List[VirtualScenario]:
            if spy:
                spy(source)
            return scenarios
    return Provider()


async def test_collect(tmp_dir: Path, module_loader: ModuleLoader):
    with given:
        spy = Mock()
        scenarios = [make_vscenario() for _ in range(2)]
        provider = make_provider(scenarios, spy)
        collector = MultiProviderScenarioCollector([provider], module_loader)

    with when:
        collected = await collector.collect(tmp_dir / "scenarios", project_dir=tmp_dir)

    with then:
        assert collected == scenarios

        source = ScenarioSource(tmp_dir / "scenarios", tmp_dir, module_loader)
        assert spy.mock_calls == [call.provide(source)]


async def test_collect_multiple_providers(tmp_dir: Path, module_loader: ModuleLoader):
    with given:
        spy = Mock()

        scenarios1 = [make_vscenario() for _ in range(2)]
        provider1 = make_provider(scenarios1, spy)

        scenarios2 = [make_vscenario()]
        provider2 = make_provider(scenarios2, spy)

        collector = MultiProviderScenarioCollector([provider1, provider2], module_loader)

    with when:
        collected = await collector.collect(tmp_dir / "scenarios", project_dir=tmp_dir)

    with then:
        assert collected == scenarios1 + scenarios2

        source = ScenarioSource(tmp_dir / "scenarios", tmp_dir, module_loader)
        assert spy.mock_calls == [call.provide(source), call.provide(source)]


async def test_register_provider(tmp_dir: Path, module_loader: ModuleLoader):
    with given:
        provider1 = make_provider([])
        provider2 = make_provider([])
        collector = MultiProviderScenarioCollector([provider1], module_loader)

    with when:
        res = collector.register_provider(provider2, registrant=Mock(wraps=Plugin))

    with then:
        assert res is None
        assert collector.providers == [provider1, provider2]


async def test_init_empty_providers(module_loader: ModuleLoader):
    with when, raises(BaseException) as exc:
        MultiProviderScenarioCollector([], module_loader)

    with then:
        assert exc.type is ValueError
        assert str(exc.value) == "At least one provider must be specified"


async def test_init_invalid_provider(module_loader: ModuleLoader):
    with when, raises(BaseException) as exc:
        MultiProviderScenarioCollector([...], module_loader)

    with then:
        assert exc.type is TypeError
        assert str(exc.value) == "All providers must be instances of ScenarioProvider"


async def test_collect_provider_exception(tmp_dir: Path, module_loader: ModuleLoader):
    with given:
        provider = make_provider([], spy=Mock(side_effect=RuntimeError("Provider error")))
        collector = MultiProviderScenarioCollector([provider], module_loader)

    with when, raises(BaseException) as exc:
        await collector.collect(tmp_dir / "scenarios", project_dir=tmp_dir)

    with then:
        assert exc.type is RuntimeError
        assert str(exc.value) == "Provider error"


async def test_collect_invalid_return_type(tmp_dir: Path, module_loader: ModuleLoader):
    with given:
        provider = make_provider(...)  # Invalid return type
        collector = MultiProviderScenarioCollector([provider], module_loader)

    with when, raises(BaseException) as exc:
        await collector.collect(tmp_dir / "scenarios", project_dir=tmp_dir)

    with then:
        assert exc.type is TypeError
        assert str(exc.value) == "Provider must return a list of VirtualScenario"


async def test_collect_invalid_scenario_type(tmp_dir: Path, module_loader: ModuleLoader):
    with given:
        provider = make_provider([make_vscenario(), ...])  # Invalid scenario type
        collector = MultiProviderScenarioCollector([provider], module_loader)

    with when, raises(BaseException) as exc_info:
        await collector.collect(tmp_dir / "scenarios", project_dir=tmp_dir)

    with then:
        assert exc_info.type is TypeError
        assert str(exc_info.value) == "Each item in the list must be a VirtualScenario"


async def test_register_invalid_provider(module_loader: ModuleLoader):
    with given:
        provider = make_provider([])
        collector = MultiProviderScenarioCollector([provider], module_loader)

    with when, raises(BaseException) as exc:
        collector.register_provider(..., registrant=Mock(wraps=Plugin))

    with then:
        assert exc.type is TypeError
        assert str(exc.value) == "Provider must be an instance of ScenarioProvider"
        assert len(collector.providers) == 1
