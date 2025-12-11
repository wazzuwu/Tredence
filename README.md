# Minimal Workflow Engine (FastAPI)

Small FastAPI backend that shows a minimal workflow/graph engine with nodes, edges, shared state, branching, and looping. Ships with a Code Review mini-agent workflow.

## Features
- Define graphs with nodes (tools) and conditional edges.
- Shared state dict flows through nodes; each tool mutates/extends it.
- Branching based on state conditions; supports simple loops.
- In-memory storage for graphs and runs.
- FastAPI endpoints: create graph, run graph, fetch run state.
- Sample workflow: Code Review mini-agent with a quality loop.

## Quickstart
1) Create venv and install (Python 3.10+):
```bash
python -m venv .venv
.\.venv\Scripts\pip install -r requirements.txt
```
2) Run the API:
```bash
.\.venv\Scripts\uvicorn.exe app.main:app --reload
```
3) Docs: http://127.0.0.1:8000/docs

Run tests:
```bash
.\.venv\Scripts\python.exe -m pytest
```

## API
- `POST /graph/create` – Register a graph definition (nodes + edges) and receive `graph_id`.
- `POST /graph/run` – Execute a graph with an initial state; returns `run_id`, final state, and execution log.
- `GET /graph/state/{run_id}` – Get current state/log for a run.

## Sample Workflow
Auto-registered Code Review mini-agent:
1. extract_functions → 2. check_complexity → 3. detect_issues → 4. suggest_improvements → 5. evaluate_quality
- Loop: If `quality_score < quality_threshold`, returns to `suggest_improvements` until threshold met.

## Structure
```
app/
  main.py
  api/routers/graph.py
  api/routers/health.py
  core/
  engine/
  workflows/
  schemas/
```

## Improvements with More Time
- Persist graphs/runs in SQLite with async SQLModel.
- WebSocket log streaming.
- Richer DSL for conditions and data validation.
- Pluggable auth + RBAC, per-tenant stores.
- Background execution with cancellation and retry policies.

## Tests
Run tests:
```bash
pytest
```

