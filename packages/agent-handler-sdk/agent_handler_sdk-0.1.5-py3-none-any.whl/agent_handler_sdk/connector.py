from typing import List, Optional, Set, Dict, Any, Union, Awaitable, Callable
from .registry import ConnectorRegistry


class Connector:
    def __init__(
        self,
        namespace: str,
        include_tools: Optional[List[str]] = None,
        include_tags: Optional[List[str]] = None,
    ):
        """
        namespace: unique prefix (e.g. "jira").
        include_tools: explicit list of fully-qualified tool names.
        include_tags: whitelist of tags to filter tools by.
        """
        self.namespace = namespace
        self.include_tools = set(include_tools) if include_tools else None
        self.include_tags = set(include_tags) if include_tags else None

    def tool(
        self,
        name: Optional[str] = None,
        desc: str = "",
        tags: Optional[List[str]] = None,
    ) -> Callable[[Callable], Callable]:
        # Wraps agent_handler_sdk.tool to inject qualified name & tags
        from .tool import tool as _tool

        def decorator(fn: Callable) -> Callable:
            qualified = f"{self.namespace}__{name or fn.__name__}"
            return _tool(name=qualified, desc=desc, tags=tags)(fn)

        return decorator

    def list_tools(self) -> List[Dict]:
        # Get all specs that match the namespace
        namespace_prefix = f"{self.namespace}__"
        specs = [t for t in ConnectorRegistry.list_tools() if t["name"].startswith(namespace_prefix)]

        # Filter by explicit tool names if specified
        if self.include_tools is not None:
            specs = [t for t in specs if t["name"] in self.include_tools]

        # Filter by tags if specified
        if self.include_tags is not None:
            # Get the tool specs from the registry to access tags
            tool_specs = {
                t.name: t for t in ConnectorRegistry._tools.values() if t.name in [spec["name"] for spec in specs]
            }

            # Filter specs based on tags
            specs = [spec for spec in specs if any(tag in self.include_tags for tag in tool_specs[spec["name"]].tags)]

        return specs

    def get_tool(self, name: str) -> Dict:
        return ConnectorRegistry.get_tool(name)

    def call_tool(self, tool_name: str, params: dict) -> Any:
        """
        Validate and invoke a registered tool by name.

        For synchronous tools, returns the result directly.
        For async tools, this will run the event loop and return the awaited result.

        Args:
            tool_name: The name of the tool to invoke
            params: Dictionary of parameters to pass to the tool

        Returns:
            The result of the tool invocation
        """
        from .invocation import invoke as _invoke

        return _invoke(tool_name, params, connector=self)

    async def call_tool_async(self, tool_name: str, params: dict) -> Any:
        """
        Validate and invoke a registered tool by name asynchronously.

        For synchronous tools, this will run them in a thread pool.
        For async tools, this will await the coroutine directly.

        Args:
            tool_name: The name of the tool to invoke
            params: Dictionary of parameters to pass to the tool

        Returns:
            The result of the tool invocation
        """
        from .invocation import invoke_async as _invoke_async

        return await _invoke_async(tool_name, params, connector=self)
