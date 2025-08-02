from typing import Any, Optional, Union, Awaitable
import asyncio
import jsonschema
from .registry import ConnectorRegistry
from .connector import Connector
from .registry import ToolSpec


def invoke(tool_name: str, params: dict, connector: Optional[Connector] = None) -> Any:
    """
    Validate and invoke a registered tool by name.
    If a Connector is provided, enforce whitelist based on that instance.

    For synchronous tools, returns the result directly.
    For async tools, this will run the event loop and return the awaited result.
    """
    spec = _get_validated_tool_spec(tool_name, params, connector)

    if spec.is_async:
        # For async functions, run the event loop
        return asyncio.run(spec.fn(**params))
    else:
        # For sync functions, call directly
        return spec.fn(**params)


async def invoke_async(tool_name: str, params: dict, connector: Optional[Connector] = None) -> Any:
    """
    Validate and invoke a registered tool by name asynchronously.
    If a Connector is provided, enforce whitelist based on that instance.

    For synchronous tools, this will run them in a thread pool.
    For async tools, this will await the coroutine directly.
    """
    spec = _get_validated_tool_spec(tool_name, params, connector)

    if spec.is_async:
        # For async functions, await directly
        return await spec.fn(**params)
    else:
        # For sync functions, run in a thread pool
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, lambda: spec.fn(**params))


def _get_validated_tool_spec(tool_name: str, params: dict, connector: Optional[Connector] = None) -> ToolSpec:
    """Helper function to get and validate a tool spec."""
    if connector:
        allowed = {t["name"] for t in connector.list_tools()}
        if tool_name not in allowed:
            raise PermissionError(f"{tool_name!r} not allowed in this context")

    spec = ConnectorRegistry.get_tool_spec(tool_name)
    jsonschema.validate(params, spec.param_schema)
    return spec
