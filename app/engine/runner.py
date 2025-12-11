from __future__ import annotations

import uuid
import inspect
from typing import Any, Awaitable, Callable, Dict, List, Optional

from .models import EdgeDefinition, GraphDefinition, RunRecord, StepLog
from .registry import ToolRegistry
from .store import GraphStore, RunStore


class GraphRunner:
    """Executes graphs sequentially with conditional branching and loops."""

    def __init__(self, registry: ToolRegistry, graph_store: GraphStore, run_store: RunStore) -> None:
        self.registry = registry
        self.graph_store = graph_store
        self.run_store = run_store

    async def run(
        self,
        graph_id: str,
        initial_state: Dict[str, Any],
        on_step: Optional[Callable[[StepLog], Awaitable[None] | None]] = None,
    ) -> RunRecord:
        """
        Execute a graph sequentially.

        on_step: optional hook invoked after each step; can be sync or async.
        Returns the completed RunRecord (or failed if exception propagates).
        """
        graph = self.graph_store.get(graph_id)
        run_id = str(uuid.uuid4())
        state: Dict[str, Any] = dict(initial_state)
        record = RunRecord(run_id=run_id, graph_id=graph_id, status="running", state=state)
        self.run_store.add(record)

        try:
            current = graph.start_node
            visited_steps: List[str] = []
            while True:
                if current not in graph.nodes:
                    raise ValueError(f"Node '{current}' not found in graph")

                tool_name = graph.nodes[current]
                input_snapshot = dict(state)
                result = await self.registry.invoke(tool_name, state)
                if not isinstance(result, dict):
                    raise TypeError(f"Tool '{tool_name}' must return a dict, got {type(result)}")
                state.update(result)

                record.log.append(
                    StepLog(
                        node=current,
                        tool=tool_name,
                        input_state=input_snapshot,
                        output_state=dict(state),
                        message=result.get("message", ""),
                    )
                )
                record.state = state
                self.run_store.update(record)
                visited_steps.append(current)

                if on_step:
                    maybe = on_step(record.log[-1])
                    if inspect.isawaitable(maybe):
                        await maybe

                next_nodes = graph.next_nodes(current, state)
                if not next_nodes:
                    record.status = "completed"
                    self.run_store.update(record)
                    return record

                # Basic loop guard: prevent runaway cycles without state change
                if len(visited_steps) > 10_000:
                    raise RuntimeError("Exceeded step limit (possible infinite loop)")

                # For now pick the first eligible next node
                current = next_nodes[0]

        except Exception as exc:  # noqa: BLE001
            record.status = "failed"
            record.error = str(exc)
            self.run_store.update(record)
            raise
