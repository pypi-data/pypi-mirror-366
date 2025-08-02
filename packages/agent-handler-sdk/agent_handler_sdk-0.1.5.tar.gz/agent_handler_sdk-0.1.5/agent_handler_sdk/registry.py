from typing import Any, Dict, Callable, List
import inspect


class ToolSpec:
    def __init__(
        self,
        name: str,
        description: str,
        fn: Callable,
        param_schema: Dict[str, Any],
        tags: List[str],
    ):
        self.name = name
        self.description = description
        self.fn = fn
        self.param_schema = param_schema
        self.tags = tags
        self.is_async = inspect.iscoroutinefunction(fn)


class ConnectorRegistry:
    _tools: Dict[str, ToolSpec] = {}

    @classmethod
    def register_tool(
        cls,
        name: str,
        description: str,
        fn: Callable,
        param_schema: Dict[str, Any],
        tags: List[str],
    ) -> None:
        if name in cls._tools:
            raise ValueError(f"Tool {name!r} already registered")
        cls._tools[name] = ToolSpec(name, description, fn, param_schema, tags)

    @classmethod
    def _format_tool_spec(cls, spec: ToolSpec) -> Dict[str, Any]:
        return {
            "name": spec.name,
            "description": spec.description,
            "input_schema": spec.param_schema,
        }

    @classmethod
    def list_tools(cls) -> List[Dict[str, Any]]:
        return [cls._format_tool_spec(t) for t in cls._tools.values()]

    @classmethod
    def get_tool(cls, name: str) -> Dict[str, Any]:
        if name not in cls._tools:
            raise ValueError(f"Tool {name!r} not found in registry")
        return cls._format_tool_spec(cls._tools[name])

    @classmethod
    def get_tool_spec(cls, name: str) -> ToolSpec:
        if name not in cls._tools:
            raise ValueError(f"Tool {name!r} not found in registry")
        return cls._tools[name]
