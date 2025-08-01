"""Prompt building for reasoning - mode-specific prompt generation."""

from typing import Any, Dict, Optional

from cogency.state import State


class Prompt:
    """Builds reasoning prompts with mode-specific logic."""

    def build(
        self,
        mode: str,
        query: str,
        context_data: Dict[str, Any],
        iteration: int,
        depth: int,
        state: State,
        identity: Optional[str] = None,
    ) -> str:
        """Build reasoning prompt with mode-specific sections."""
        from cogency.config import MAX_TOOL_CALLS

        # Get context components
        tool_registry = context_data["tool_registry"]
        reasoning_context = context_data["reasoning_context"]
        memory_context = context_data["memory_context"]
        workspace_context = context_data["workspace_context"]

        # Build mode-specific context
        if mode == "deep":
            reasoning_phases = self._build_deep_phases(depth)
            mode_context = self._build_deep_context(
                iteration, depth, memory_context, workspace_context, reasoning_context
            )
        else:  # fast mode
            reasoning_phases = self._build_fast_phases()
            mode_context = self._build_fast_context(
                memory_context, workspace_context, reasoning_context
            )

        # Build base prompt
        prompt = f"""
{mode.upper()}: {"Structured reasoning" if mode == "deep" else "Direct execution"} for query: {query}

CRITICAL: Output ONE JSON object for THIS ITERATION ONLY. Do not anticipate future steps.

JSON Response Format:
{{
  "thinking": "What am I trying to accomplish? What's my approach to this problem?",{
        '"reflect": "What worked/failed in previous actions? What gaps remain?",'
        if mode == "deep"
        else ""
    }{'"plan": "What specific tools to use next and expected outcomes?",' if mode == "deep" else ""}
  "tool_calls": [
    {{"name": "tool_a", "args": {{"param": "value"}}}},
    {{"name": "tool_b", "args": {{"param": "value"}}}},
    {{"name": "tool_c", "args": {{"param": "value"}}}}
  ],
  "switch_to": null,
  "switch_why": null,
  "workspace_update": {{
    "objective": "Clear problem statement: What is the main goal?",
    "assessment": "Current situation: What information have we gathered?",
    "approach": "Current strategy: What method are we using?",
    "observations": "Key findings: What important insights have we found?"
  }}
}}

IMPORTANT: All {MAX_TOOL_CALLS} tool calls must be in ONE tool_calls array, not separate JSON objects.

WORKSPACE UPDATE FIELDS:
- objective: Clear problem statement - what are we trying to achieve?
- assessment: Current situation - what facts/context do we have?
- approach: Strategy being used - how are we solving this?
- observations: Key insights - what important findings have emerged?

When done: {{"thinking": "explanation", "tool_calls": [], "switch_to": null, "switch_why": null, "workspace_update": {{"objective": "updated objective", "assessment": "what we learned", "approach": "approach used", "observations": "key insights found"}}}}

TOOLS:
{tool_registry}

{mode_context}

{reasoning_phases}

- Empty tool_calls array ([ ]) if query fully answered or no progress possible
- If original query has been fully resolved, say so explicitly and return tool_calls: []
- LIMIT: Maximum {MAX_TOOL_CALLS} tool calls per iteration to avoid JSON parsing issues
"""

        # Add identity if provided
        if identity:
            prompt = f"{identity}\n\n{prompt}"

        return prompt

    def _build_deep_phases(self, depth: int) -> str:
        """Build deep reasoning phase instructions."""
        return f"""
REASONING PHASES:
🤔 REFLECT: Review completed actions and their DETAILED results - what information do you already have? What gaps remain?
📋 PLAN: Choose NEW tools that address remaining gaps - avoid repeating successful actions
🎯 EXECUTE: Run planned tools sequentially when they address different aspects

RECOVERY ACTIONS:
- Tool parameter errors → Check required vs optional parameters in schema
- No results from tools → Try different parameters or alternative approaches
- Information conflicts → Use additional tools to verify or synthesize  
- Use the DETAILED action history to understand what actually happened, not just success/failure
- Avoid repeating successful tool calls - check action history first

DOWNSHIFT to FAST if:
- Simple datetime request using time tool
- Direct search with obvious keywords
- Single-step action with clear tool choice
- Approaching depth limit ({depth} iterations) - prioritize direct execution
- Complex analysis not yielding progress after 2+ iterations

Examples:
switch_to: "fast", switch_why: "Query simplified to direct search"
switch_to: "fast", switch_why: "Single tool execution sufficient"
switch_to: "fast", switch_why: "Approaching depth limit, need direct action"
"""

    def _build_fast_phases(self) -> str:
        """Build fast reasoning phase instructions."""
        return """
CRITICAL STOP CONDITIONS:
- If you see previous attempts that ALREADY answered the query → tool_calls: []
- If query is fully satisfied by previous results → tool_calls: []  
- If no tool can help with this query → tool_calls: []
- If repeating same failed action → tool_calls: []

GUIDANCE:
- FIRST: Review previous attempts to avoid repeating actions
- Use tools only if query needs MORE information

ESCALATE to DEEP if encountering:
- Tool results conflict and need synthesis
- Multi-step reasoning chains required  
- Ambiguous requirements need breakdown
- Complex analysis beyond direct execution

Examples:
switch_to: "deep", switch_why: "Search results contradict, need analysis"
switch_to: "deep", switch_why: "Multi-step calculation required"
"""

    def _build_deep_context(
        self,
        iteration: int,
        depth: int,
        memory_context: str,
        workspace_context: str,
        reasoning_context: str,
    ) -> str:
        """Build deep mode context section."""
        return f"""
CONTEXT:
Iteration {iteration}/{depth} - Review completed actions to avoid repetition

{memory_context}COGNITIVE WORKSPACE:
{workspace_context}

PREVIOUS ACTIONS:
{reasoning_context}
"""

    def _build_fast_context(
        self, memory_context: str, workspace_context: str, reasoning_context: str
    ) -> str:
        """Build fast mode context section."""
        return f"""
{memory_context}COGNITIVE WORKSPACE:
{workspace_context}

PREVIOUS CONTEXT:
{reasoning_context if reasoning_context else "Initial execution - no prior actions"}
"""
