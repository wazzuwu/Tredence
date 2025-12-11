from __future__ import annotations

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, validator


class ConditionSpec(BaseModel):
    key: str
    op: str = Field(description="Operator: eq, ne, gt, gte, lt, lte, contains")
    value: Any

    @validator("op")
    def validate_op(cls, v: str) -> str:
        allowed = {"eq", "ne", "gt", "gte", "lt", "lte", "contains"}
        if v not in allowed:
            raise ValueError(f"Unsupported operator '{v}'")
        return v


class NodeSpec(BaseModel):
    name: str
    tool: str


class EdgeSpec(BaseModel):
    source: str
    target: str
    condition: Optional[ConditionSpec] = None


class GraphCreateRequest(BaseModel):
    graph_id: Optional[str] = Field(default=None, description="Leave empty to auto-generate")
    start_node: str
    nodes: List[NodeSpec]
    edges: List[EdgeSpec]
    metadata: Dict[str, Any] = Field(default_factory=dict)


class GraphCreateResponse(BaseModel):
    graph_id: str


class GraphRunRequest(BaseModel):
    graph_id: str
    initial_state: Dict[str, Any] = Field(default_factory=dict)


class ExecutionLogEntry(BaseModel):
    node: str
    tool: str
    input_state: Dict[str, Any]
    output_state: Dict[str, Any]
    message: str = ""


class GraphRunResponse(BaseModel):
    run_id: str
    graph_id: str
    status: str
    state: Dict[str, Any]
    log: List[ExecutionLogEntry]
    error: Optional[str] = None
