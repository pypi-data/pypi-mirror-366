import pytest
from {name}_connector import {name}
from agent_handler_sdk.invocation import invoke

@pytest.mark.parametrize("tool_name,params,expected", [
    ("{name}__example", {{}}, {{"status": "ok"}}),
])
def test_{name}_operations(tool_name, params, expected):
    # Directly invoke tools using the SDK
    result = invoke(tool_name, params, connector={name})
    assert result == expected

@pytest.mark.parametrize("tool_name,params,expected", [
    ("{name}__example", {{}}, {{"status": "ok"}}),
])
def test_{name}_operations_with_connector(tool_name, params, expected):
    # Invoke tools using the Connector
    result = {name}.call_tool(tool_name, params)
    assert result == expected
