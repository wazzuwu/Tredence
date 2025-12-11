from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class Condition:
    key: str
    op: str
    value: Any

    def evaluate(self, state: Dict[str, Any]) -> bool:
        lhs = state.get(self.key)
        op = self.op.lower()
        rhs = self.value
        # Support referencing another state key via "$other_key"
        if isinstance(rhs, str) and rhs.startswith("$"):
            rhs = state.get(rhs[1:], rhs)
        if op == "eq":
            return lhs == rhs
        if op == "ne":
            return lhs != rhs
        if op == "gt":
            return lhs > rhs
        if op == "gte":
            return lhs >= rhs
        if op == "lt":
            return lhs < rhs
        if op == "lte":
            return lhs <= rhs
        if op == "contains":
            return isinstance(lhs, (list, str, dict)) and rhs in lhs
        raise ValueError(f"Unsupported operator: {self.op}")


@dataclass
class EdgeDefinition:
    source: str
    target: str
    condition: Optional[Condition] = None


@dataclass
class GraphDefinition:
    graph_id: str
    start_node: str
    nodes: Dict[str, str]  # node name -> tool name
    edges: List[EdgeDefinition]
    metadata: Dict[str, Any] = field(default_factory=dict)

    def next_nodes(self, current: str, state: Dict[str, Any]) -> List[str]:
        """Return eligible next nodes based on conditions."""
        candidates: List[str] = []
        for edge in self.edges:
            if edge.source != current:
                continue
            if edge.condition is None or edge.condition.evaluate(state):
                candidates.append(edge.target)
        return candidates


@dataclass
class StepLog:
    node: str
    tool: str
    input_state: Dict[str, Any]
    output_state: Dict[str, Any]
    message: str = ""


@dataclass
class RunRecord:
    run_id: str
    graph_id: str
    status: str  # running, completed, failed
    state: Dict[str, Any]
    log: List[StepLog] = field(default_factory=list)
    error: Optional[str] = None
