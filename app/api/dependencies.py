from __future__ import annotations

from fastapi import Depends

from app.engine.registry import ToolRegistry
from app.engine.runner import GraphRunner
from app.engine.store import GraphStore, RunStore


# Global singletons for this simple assignment
_tool_registry = ToolRegistry()
_graph_store = GraphStore()
_run_store = RunStore()
_runner = GraphRunner(_tool_registry, _graph_store, _run_store)


def get_tool_registry() -> ToolRegistry:
    return _tool_registry


def get_graph_store() -> GraphStore:
    return _graph_store


def get_run_store() -> RunStore:
    return _run_store


def get_runner(
    registry: ToolRegistry = Depends(get_tool_registry),
    graph_store: GraphStore = Depends(get_graph_store),
    run_store: RunStore = Depends(get_run_store),
) -> GraphRunner:
    # Using the singleton runner here keeps things simple for the exercise
    return _runner
