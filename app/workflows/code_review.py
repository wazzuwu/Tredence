from __future__ import annotations

import re
from statistics import mean
from typing import Any, Dict

from app.engine.models import Condition, EdgeDefinition, GraphDefinition
from app.engine.registry import ToolRegistry
from app.engine.store import GraphStore


def extract_functions(state: Dict[str, Any]) -> Dict[str, Any]:
    code = state.get("code", "")
    functions = re.findall(r"def\s+(\w+)\s*\(", code)
    lines = code.splitlines()
    return {
        "functions": functions,
        "line_count": len(lines),
        "message": f"Found {len(functions)} functions",
    }


def check_complexity(state: Dict[str, Any]) -> Dict[str, Any]:
    lines = state.get("line_count", 0)
    fn_count = max(len(state.get("functions", [])), 1)
    avg_len = lines / fn_count
    complexity_score = min(1.0, avg_len / 50)
    return {
        "avg_fn_length": avg_len,
        "complexity_score": complexity_score,
        "message": "Computed complexity",
    }


def detect_issues(state: Dict[str, Any]) -> Dict[str, Any]:
    issues = []
    code = state.get("code", "")
    if "TODO" in code:
        issues.append("Contains TODOs")
    if "print(" in code:
        issues.append("Debug prints present")
    if state.get("avg_fn_length", 0) > 80:
        issues.append("Functions too long")
    issue_count = len(issues)
    return {
        "issues": issues,
        "issue_count": issue_count,
        "message": f"Detected {issue_count} issues",
    }


def suggest_improvements(state: Dict[str, Any]) -> Dict[str, Any]:
    suggestions = [
        "Break down long functions into smaller units.",
        "Replace debug prints with structured logging.",
        "Document edge cases and failure modes.",
    ]
    if state.get("issue_count", 0) == 0:
        suggestions.append("Looks good overall. Consider adding more tests.")
    return {
        "suggestions": suggestions,
        "message": "Generated suggestions",
    }


def evaluate_quality(state: Dict[str, Any]) -> Dict[str, Any]:
    complexity = state.get("complexity_score", 0)
    issues = state.get("issue_count", 0)
    suggestions = len(state.get("suggestions", []))
    quality_threshold = state.get("quality_threshold", 0.75)

    quality_score = max(0.0, 1.0 - complexity - 0.1 * issues + 0.01 * suggestions)
    state_update = {
        "quality_score": round(quality_score, 3),
        "quality_threshold": quality_threshold,
    }
    if quality_score >= quality_threshold:
        state_update["ready_to_ship"] = True
        state_update["message"] = "Quality threshold met"
    else:
        state_update["ready_to_ship"] = False
        state_update["message"] = "Quality below threshold; iterating"
    return state_update


def register_code_review_workflow(registry: ToolRegistry, graph_store: GraphStore) -> str:
    registry.register("extract_functions", extract_functions)
    registry.register("check_complexity", check_complexity)
    registry.register("detect_issues", detect_issues)
    registry.register("suggest_improvements", suggest_improvements)
    registry.register("evaluate_quality", evaluate_quality)

    graph_id = "code_review"
    graph = GraphDefinition(
        graph_id=graph_id,
        start_node="extract",
        nodes={
            "extract": "extract_functions",
            "complexity": "check_complexity",
            "issues": "detect_issues",
            "suggest": "suggest_improvements",
            "evaluate": "evaluate_quality",
        },
        edges=[
            EdgeDefinition(source="extract", target="complexity"),
            EdgeDefinition(source="complexity", target="issues"),
            EdgeDefinition(source="issues", target="suggest"),
            EdgeDefinition(source="suggest", target="evaluate"),
            # Loop if quality_score < quality_threshold (dynamic via $quality_threshold)
            EdgeDefinition(
                source="evaluate",
                target="suggest",
                condition=Condition(key="quality_score", op="lt", value="$quality_threshold"),
            ),
        ],
        metadata={"example": "code_review"},
    )
    graph_store.add(graph)
    return graph_id
