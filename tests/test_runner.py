import pytest
from fastapi.testclient import TestClient

from app.engine.registry import ToolRegistry
from app.engine.runner import GraphRunner
from app.engine.store import GraphStore, RunStore
from app.workflows.code_review import register_code_review_workflow
from app.main import app


@pytest.mark.asyncio
async def test_code_review_workflow_completes():
    registry = ToolRegistry()
    graph_store = GraphStore()
    run_store = RunStore()
    runner = GraphRunner(registry, graph_store, run_store)

    graph_id = register_code_review_workflow(registry, graph_store)

    record = await runner.run(
        graph_id,
        {
            "code": """\
            def foo():
                print('hello')
            def bar():
                pass
            """,
            "quality_threshold": 0.6,
        },
    )

    assert record.status == "completed"
    assert "quality_score" in record.state
    assert len(record.log) >= 5
    assert record.state.get("quality_score") >= 0


@pytest.mark.asyncio
async def test_runner_invokes_on_step_callback():
    registry = ToolRegistry()
    graph_store = GraphStore()
    run_store = RunStore()
    runner = GraphRunner(registry, graph_store, run_store)

    graph_id = register_code_review_workflow(registry, graph_store)

    seen_nodes = []

    async def on_step(step):
        seen_nodes.append(step.node)

    await runner.run(
        graph_id,
        {
            "code": "def foo():\n    return 1",
            "quality_threshold": 0.5,
        },
        on_step=on_step,
    )

    assert seen_nodes[0] == "extract"
    assert "evaluate" in seen_nodes


def test_create_graph_rejects_unknown_edges():
    client = TestClient(app)
    payload = {
        "start_node": "start",
        "nodes": [{"name": "start", "tool": "extract_functions"}],
        "edges": [
            {"source": "start", "target": "missing"},
        ],
    }
    resp = client.post("/graph/create", json=payload)
    assert resp.status_code == 400
    assert "edges" in resp.json().get("detail", "")
