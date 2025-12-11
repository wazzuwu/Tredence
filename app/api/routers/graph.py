from __future__ import annotations

import uuid
from fastapi import APIRouter, Depends, HTTPException

from app.api.dependencies import get_graph_store, get_runner, get_run_store
from app.engine.models import Condition, EdgeDefinition, GraphDefinition
from app.engine.runner import GraphRunner
from app.engine.store import GraphStore, RunStore
from app.schemas.graph import (
    ExecutionLogEntry,
    GraphCreateRequest,
    GraphCreateResponse,
    GraphRunRequest,
    GraphRunResponse,
)
from app.schemas.run import RunStateResponse

router = APIRouter(prefix="/graph", tags=["graph"])


@router.post("/create", response_model=GraphCreateResponse)
async def create_graph(
    payload: GraphCreateRequest,
    graph_store: GraphStore = Depends(get_graph_store),
) -> GraphCreateResponse:
    graph_id = payload.graph_id or str(uuid.uuid4())

    node_map = {node.name: node.tool for node in payload.nodes}
    edges: list[EdgeDefinition] = []
    for edge in payload.edges:
        if edge.source not in node_map or edge.target not in node_map:
            raise HTTPException(status_code=400, detail="edges must reference defined nodes")
        cond = None
        if edge.condition:
            cond = Condition(key=edge.condition.key, op=edge.condition.op, value=edge.condition.value)
        edges.append(EdgeDefinition(source=edge.source, target=edge.target, condition=cond))

    if payload.start_node not in node_map:
        raise HTTPException(status_code=400, detail="start_node must exist in nodes")

    graph = GraphDefinition(
        graph_id=graph_id,
        start_node=payload.start_node,
        nodes=node_map,
        edges=edges,
        metadata=payload.metadata,
    )
    graph_store.add(graph)
    return GraphCreateResponse(graph_id=graph_id)


@router.post("/run", response_model=GraphRunResponse)
async def run_graph(
    request: GraphRunRequest,
    runner: GraphRunner = Depends(get_runner),
) -> GraphRunResponse:
    try:
        record = await runner.run(request.graph_id, request.initial_state)
    except KeyError as exc:  # noqa: PERF203
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    log = [
        ExecutionLogEntry(
            node=entry.node,
            tool=entry.tool,
            input_state=entry.input_state,
            output_state=entry.output_state,
            message=entry.message,
        )
        for entry in record.log
    ]
    return GraphRunResponse(
        run_id=record.run_id,
        graph_id=record.graph_id,
        status=record.status,
        state=record.state,
        log=log,
        error=record.error,
    )


@router.get("/state/{run_id}", response_model=RunStateResponse)
async def get_run_state(
    run_id: str,
    run_store: RunStore = Depends(get_run_store),
) -> RunStateResponse:
    try:
        record = run_store.get(run_id)
    except KeyError as exc:  # noqa: PERF203
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    log = [
        ExecutionLogEntry(
            node=entry.node,
            tool=entry.tool,
            input_state=entry.input_state,
            output_state=entry.output_state,
            message=entry.message,
        )
        for entry in record.log
    ]
    return RunStateResponse(
        run_id=record.run_id,
        graph_id=record.graph_id,
        status=record.status,
        state=record.state,
        log=log,
        error=record.error,
    )


