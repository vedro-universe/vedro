import json
from asyncio import iscoroutinefunction
from collections import deque
from dataclasses import dataclass, field
from functools import wraps
from typing import Any, Deque, Dict, List, Type, Union

from vedro.core import Dispatcher, MemoryArtifact, Plugin, PluginConfig
from vedro.events import ScenarioFailedEvent, ScenarioPassedEvent, ScenarioRunEvent

__all__ = ("ContextTracer", "ContextTracerPlugin", "context",)


@dataclass
class Node:
    name: str
    module: str
    children: List["Node"] = field(default_factory=list)


_call_stack: Deque[Node] = deque()
_call_forest: Deque[Node] = deque()


def context(fn, *, call_forest: Deque[Node] = _call_forest, call_stack: Deque[Node] = _call_stack):
    setattr(fn, "__vedro__context__", True)

    @wraps(fn)
    async def async_wrapper(*args, **kwargs):
        node = Node(name=fn.__name__, module=fn.__module__)
        if not call_stack:
            call_forest.append(node)
        else:
            call_stack[-1].children.append(node)

        call_stack.append(node)
        try:
            return await fn(*args, **kwargs)
        finally:
            call_stack.pop()

    @wraps(fn)
    def sync_wrapper(*args, **kwargs):
        node = Node(name=fn.__name__, module=fn.__module__)
        if not call_stack:
            call_forest.append(node)
        else:
            call_stack[-1].children.append(node)

        call_stack.append(node)
        try:
            return fn(*args, **kwargs)
        finally:
            call_stack.pop()

    return async_wrapper if iscoroutinefunction(fn) else sync_wrapper


class ContextTracerPlugin(Plugin):
    def __init__(self, config: Type["ContextTracer"], *,
                 call_forest: Deque[Node] = _call_forest,
                 call_stack: Deque[Node] = _call_stack) -> None:
        super().__init__(config)
        self._call_forest = call_forest
        self._call_stack = call_stack

    def subscribe(self, dispatcher: Dispatcher) -> None:
        dispatcher.listen(ScenarioRunEvent, self.on_scenario_run) \
                  .listen(ScenarioPassedEvent, self.on_scenario_end) \
                  .listen(ScenarioFailedEvent, self.on_scenario_end)

    def on_scenario_run(self, event: ScenarioRunEvent) -> None:
        self._call_forest.clear()
        self._call_stack.clear()

    def on_scenario_end(self, event: Union[ScenarioPassedEvent, ScenarioFailedEvent]) -> None:
        if self._call_forest:
            context_call_tree = json.dumps(
                [self._serialize_node(node) for node in self._call_forest],
                ensure_ascii=False,
                indent=4
            )
            artifact = MemoryArtifact(
                "context-call-tree.json",
                "application/json",
                context_call_tree.encode()
            )
            event.scenario_result.attach(artifact)

    def _serialize_node(self, node: Node) -> Dict[str, Any]:
        return {
            "name": node.name,
            "module": node.module,
            "children": [self._serialize_node(child) for child in node.children]
        }


class ContextTracer(PluginConfig):
    plugin = ContextTracerPlugin
    description = ""
