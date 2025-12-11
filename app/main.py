from __future__ import annotations

from fastapi import FastAPI

from app.api import dependencies
from app.api.routers import graph, health
from app.core.config import get_settings
from app.core.logging import configure_logging
from app.workflows.code_review import register_code_review_workflow

configure_logging()
settings = get_settings()

app = FastAPI(title=settings.app_name, debug=settings.debug)
app.include_router(health.router)
app.include_router(graph.router)

# Register sample workflow at startup
register_code_review_workflow(
    registry=dependencies.get_tool_registry(),
    graph_store=dependencies.get_graph_store(),
)


@app.get("/")
async def root() -> dict[str, str]:
    return {"message": "Workflow engine running", "example_graph": "code_review"}
