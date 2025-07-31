"""Preprocess node - routing, memory extraction, tool filtering."""

from typing import List, Optional

from cogency.decorators import phase
from cogency.phases import Phase
from cogency.services import LLM
from cogency.state import State
from cogency.tools import Tool, build_registry
from cogency.types.preprocessed import Preprocessed
from cogency.utils import is_simple_query, parse_json
from cogency.utils.response import format_response


class Preprocess(Phase):
    def __init__(self, llm, tools, memory, identity=None):
        super().__init__(
            preprocess,
            llm=llm,
            tools=tools,
            memory=memory,
            identity=identity,
        )


@phase.preprocess()
async def preprocess(
    state: State,
    notifier,
    llm: LLM,
    tools: List[Tool],
    memory,  # Impression instance or None
    identity: Optional[str] = None,
) -> Optional[str]:
    """Preprocess: routing decisions, memory extraction, tool selection."""
    query = state.query
    # Direct access to state properties - no context wrapper needed
    user_id = state.user_id

    # Pre-React phases will stream via MEMORIZE and TOOLING messages below

    # Use LLM for intelligent analysis when we have tools (memory + complexity + filtering)
    if tools and len(tools) > 0:
        registry_lite = build_registry(tools, lite=True)

        # Skip preprocessing state - no ceremony

        # Pragmatic heuristic: Simple queries likely don't need deep reasoning
        # Safety check: ensure query is string
        query_str = query if isinstance(query, str) else str(query)
        suggested_mode = "fast" if is_simple_query(query_str) else None

        # Single LLM call: routing + memory + tool selection + complexity analysis
        hint_section = (
            "\nHINT: This appears to be a simple query, consider fast mode."
            if suggested_mode == "fast"
            else ""
        )

        prompt_preprocess = f"""You are a preprocessing agent responsible for query classification before reasoning begins.

Query: "{query}"

JSON Response Format:
{{
  "memory": "extracted user fact relevant for persistence" | null,
  "tags": ["topical", "categories"] | null,
  "memory_type": "fact",
  "mode": "fast" | "deep", 
  "selected_tools": ["tool1", "tool2"] | [],
  "reasoning": "brief justification of complexity and tool choices"
}}{hint_section}

ANALYSIS FRAMEWORK:
🧠 MEMORY: Extract factual user statements worth remembering (goals, context, identity) or null
🎯 COMPLEXITY: Classify task complexity using concrete signals:
   - FAST: Single factual lookup, basic calculation, direct command, simple question
   - DEEP: Multiple sources needed, comparison/synthesis, creative generation, coding tasks

🔧 TOOLS: Select tools that directly address query's core execution needs:
{registry_lite}

FIELD DEFINITIONS:
- memory: Extractive facts from user ("building a React app", "lives in London") 
- tags: Interpretive categories for later use ("ai", "coding", "travel")
- selected_tools: Subset of available tools needed for likely execution
- reasoning: How you classified complexity and selected tools

Example:
```json
{{
  "memory": "User mentioned working on a monorepo project called Folio",
  "tags": ["coding", "architecture"], 
  "memory_type": "fact",
  "mode": "deep",
  "selected_tools": ["files", "search"],
  "reasoning": "Software architecture query requires multiple steps and file analysis"
}}
```"""

        # @safe.preprocess() auto-unwraps Results - clean boundary discipline
        llm_result = await llm.run([{"role": "user", "content": prompt_preprocess}])
        from resilient_result import unwrap

        llm_response = unwrap(llm_result)  # Unwrap LLM Result first
        parsed_data = unwrap(parse_json(llm_response))
        result = Preprocessed(**parsed_data)

        # Chain 1: Save extracted memory if not null/empty and memory is enabled
        if memory and result.memory:
            # Stream memory extraction using clean API
            memory_content = result.memory
            # Clean memory summary - avoid awkward truncation
            if memory_content and len(memory_content) > 60:
                # Find a natural break point near 60 chars
                break_point = memory_content.rfind(" ", 40, 60)
                if break_point == -1:
                    break_point = 60
                output_content = f"{memory_content[:break_point]}..."
            else:
                output_content = memory_content
            await notifier("preprocess", state="memory_saved", content_preview=output_content)

            # Learn from extracted memory content (LLM-native Memory)
            if memory_content and memory:
                await memory.remember(memory_content, human=True)

        # Chain 2: Filter tools based on LLM selection and check for early response
        selected_tools = result.selected_tools
        if selected_tools is not None:  # LLM explicitly provided selected_tools
            if not selected_tools:  # LLM explicitly selected no tools
                filtered_tools = []
                # If LLM explicitly selected no tools, we might have a direct answer
                # For simple queries, return the query as the response to bypass further processing
                query_str = query if isinstance(query, str) else str(query)
                if is_simple_query(query_str):
                    # Let the LLM provide a direct response to simple queries
                    simple_prompt = f"Answer this simple question directly: {query}"
                    simple_result = await llm.run([{"role": "user", "content": simple_prompt}])
                    direct_answer = unwrap(simple_result)
                    return format_response(direct_answer.strip(), identity=identity)
            else:
                selected_names = set(selected_tools)
                filtered_tools = [tool for tool in tools if tool.name in selected_names]
        else:  # LLM did not provide selected_tools, fallback to all tools
            filtered_tools = tools

        # Trace execution path decisions
        if filtered_tools:
            if len(filtered_tools) < len(tools):
                # Tool filtering decision affects behavior
                await notifier(
                    "preprocess",
                    state="filtered",
                    selected_tools=len(filtered_tools),
                    total_tools=len(tools),
                )
            elif len(filtered_tools) == 1:
                # Single tool triggers direct execution
                await notifier("preprocess", state="direct", tool_count=1)
            else:
                # Multi-tool triggers ReAct loop
                await notifier("preprocess", state="react", tool_count=len(filtered_tools))
    else:
        # Simple case: no tools available, provide direct response
        filtered_tools = []  # No tools to filter if initial 'tools' list is empty

        # For simple queries with no tools, provide direct response
        query_str = query if isinstance(query, str) else str(query)
        if is_simple_query(query_str):
            simple_prompt = f"Answer this simple question directly: {query}"
            simple_result = await llm.run([{"role": "user", "content": simple_prompt}])
            direct_answer = unwrap(simple_result)
            return format_response(direct_answer.strip(), identity=identity)

        # Tool selection is now silent - no ceremony

    # Chain 3: Prepare tools for ReAct (remove memorize, keep recall) - inline, no ceremony
    prepared_tools = [tool for tool in filtered_tools if tool.name != "memorize"]
    selected_tools = (
        prepared_tools if prepared_tools else []
    )  # Use empty list if no tools selected/prepared

    # Update flow state - clean routing via early returns
    state.selected_tools = selected_tools
    state.mode = result.mode if "result" in locals() else "fast"
    state.iteration = 0

    # No early return, continue to reason phase
    return None
