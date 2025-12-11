from __future__ import annotations

from typing import Any, Dict, List, Optional
from pydantic import BaseModel
from .graph import ExecutionLogEntry


class RunStateResponse(BaseModel):
    run_id: str
    graph_id: str
    status: str
    state: Dict[str, Any]
    log: List[ExecutionLogEntry]
    error: Optional[str] = None
