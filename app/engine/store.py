from __future__ import annotations

from typing import Dict
from .models import GraphDefinition, RunRecord


class GraphStore:
    """In-memory graph registry."""

    def __init__(self) -> None:
        self._graphs: Dict[str, GraphDefinition] = {}

    def add(self, graph: GraphDefinition) -> None:
        self._graphs[graph.graph_id] = graph

    def get(self, graph_id: str) -> GraphDefinition:
        if graph_id not in self._graphs:
            raise KeyError(f"Graph '{graph_id}' not found")
        return self._graphs[graph_id]

    def list_ids(self) -> list[str]:
        return sorted(self._graphs.keys())


class RunStore:
    """In-memory run store."""

    def __init__(self) -> None:
        self._runs: Dict[str, RunRecord] = {}

    def add(self, record: RunRecord) -> None:
        self._runs[record.run_id] = record

    def get(self, run_id: str) -> RunRecord:
        if run_id not in self._runs:
            raise KeyError(f"Run '{run_id}' not found")
        return self._runs[run_id]

    def update(self, record: RunRecord) -> None:
        self._runs[record.run_id] = record
