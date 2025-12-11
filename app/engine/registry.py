from __future__ import annotations

from typing import Any, Awaitable, Callable, Dict
import inspect

ToolFn = Callable[[dict[str, Any]], Awaitable[dict[str, Any]] | dict[str, Any]]


class ToolRegistry:
    """Simple registry for node tools."""

    def __init__(self) -> None:
        self._tools: Dict[str, ToolFn] = {}

    def register(self, name: str, fn: ToolFn) -> None:
        if not callable(fn):
            raise TypeError(f"Tool {name} is not callable")
        self._tools[name] = fn

    def get(self, name: str) -> ToolFn:
        if name not in self._tools:
            raise KeyError(f"Tool '{name}' not found")
        return self._tools[name]

    def list_tools(self) -> list[str]:
        return sorted(self._tools.keys())

    async def invoke(self, name: str, state: dict[str, Any]) -> dict[str, Any]:
        tool = self.get(name)
        result = tool(state)
        if inspect.isawaitable(result):
            return await result  # type: ignore[return-value]
        return result
