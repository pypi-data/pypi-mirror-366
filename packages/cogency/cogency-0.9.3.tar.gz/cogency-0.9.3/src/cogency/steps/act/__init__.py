"""Act node - pure tool execution."""

import logging
import time
from typing import List, Optional

from cogency.state import State
from cogency.tools import Tool

from .executor import execute_tools

logger = logging.getLogger(__name__)


async def act(state: State, notifier, tools: List[Tool]) -> Optional[str]:
    """Act: execute tools based on reasoning decision."""
    time.time()

    tool_call_str = state.tool_calls
    if not tool_call_str:
        return None

    # Direct access to state properties - no context wrapper needed
    selected_tools = state.selected_tools or tools

    # Tool calls come from reason node as parsed list
    tool_calls = state.tool_calls
    if not tool_calls or not isinstance(tool_calls, list):
        return None

    # Start acting state
    # Acting is implicit - tool execution shows progress

    tool_tuples = [
        (call["name"], call["args"]) if isinstance(call, dict) else (call.name, call.args)
        for call in tool_calls
    ]

    # Let @safe.act() handle all tool execution errors, retries, and recovery
    tool_result = await execute_tools(tool_tuples, selected_tools, state, notifier)

    # Tool result received - debug info available via state if needed

    # Store results using State methods (schema-compliant)
    if tool_result.success and tool_result.data:
        results_data = tool_result.data
        successes = results_data.get("results", [])
        failures = results_data.get("errors", [])

        # Processing tool results silently

        # Add successful tool results
        for success in successes:
            state.add_tool_result(
                name=success["tool_name"],
                args=success["args"],
                result=success["result_object"],
            )

        # Add failed tool results
        for failure in failures:
            state.add_tool_result(
                name=failure["tool_name"],
                args=failure["args"],
                result=failure["result_object"],
            )

    return None
