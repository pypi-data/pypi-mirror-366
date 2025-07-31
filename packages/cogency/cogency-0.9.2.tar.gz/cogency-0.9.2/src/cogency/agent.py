"""Main Agent class - cognitive orchestration with streaming, memory, and tool integration."""

import asyncio
from typing import Any, AsyncIterator, Dict, List, Literal, Optional, Union

from cogency import decorators
from cogency.config import MemoryConfig, ObserveConfig, PersistConfig, RobustConfig, setup_config
from cogency.mcp import setup_mcp
from cogency.memory import Memory
from cogency.notify import Formatter, Notifier, setup_formatter
from cogency.persist.utils import get_state
from cogency.phases import setup_phases
from cogency.services import LLM, Embed, setup_embed, setup_llm
from cogency.state import State
from cogency.tools import Tool, setup_tools
from cogency.utils import validate_query


class Agent:
    """Cognitive agent with streaming execution, tool integration, memory and adaptive reasoning"""

    def __init__(
        self,
        name: str = "cogency",
        *,  # Force keyword-only arguments
        # Backend Systems (things with constructors)
        llm: Optional[LLM] = None,
        embed: Optional[Embed] = None,
        tools: Optional[List[Tool]] = None,
        memory: Union[bool, MemoryConfig] = False,
        # Agent Personality
        identity: Optional[str] = None,
        output_schema: Optional[Dict[str, Any]] = None,
        # Execution Control
        mode: Literal["fast", "deep", "adapt"] = "adapt",
        depth: int = 10,
        # User Feedback (simple flags + advanced v2 system)
        notify: bool = True,
        debug: bool = False,
        formatter: Optional[Formatter] = None,
        on_notify: Optional[callable] = None,
        # System Behaviors (@phase decorator control)
        robust: Union[bool, RobustConfig] = True,
        observe: Union[bool, ObserveConfig] = False,
        persist: Union[bool, PersistConfig] = False,
        # Integrations
        mcp: bool = False,
    ) -> None:
        self.name = name
        self.depth = depth

        # User feedback flags (simple interface)
        self.notify = notify
        self.debug = debug

        # v2 notification system (advanced interface)
        self.on_notify = on_notify
        self.formatter = formatter or setup_formatter(notify, debug)
        self.notifier = Notifier(self.formatter, self.on_notify)

        # Mode - direct assignment, no ceremony
        self.mode = mode

        # Setup services with auto-detection
        self.llm = setup_llm(llm)
        self.embed = setup_embed(embed)
        self.tools = setup_tools(tools, None)

        # Config setup with auto-detection
        from cogency.persist import setup_persistence

        persist_config = setup_config(PersistConfig, persist, store=persist)
        memory_config = setup_config(MemoryConfig, memory)

        self.config = type(
            "Config",
            (),
            {
                "robust": setup_config(RobustConfig, robust),
                "observe": setup_config(ObserveConfig, observe),
                "persist": persist_config,
                "memory": memory_config,
            },
        )()

        # Setup memory with config
        if memory_config:
            store = memory_config.store or (persist_config.store if persist_config else None)
            self.memory = Memory(self.llm, store=store, user_id=memory_config.user_id)
            self.memory.synthesis_threshold = memory_config.synthesis_threshold
        else:
            self.memory = None

        # Setup persistence instance for agent use
        self.persistence = setup_persistence(persist_config)

        # Configure decorators with proper persistence config
        decorators.configure(
            robust=self.config.robust,
            observe=self.config.observe,
            persistence=persist_config,
        )

        # Agent personality
        self.identity = identity or ""
        self.output_schema = output_schema

        # State management
        self.user_states: dict[str, State] = {}
        self.last_state: Optional[dict] = None  # Store for traces()

        # Setup phases with zero ceremony
        self.phases = setup_phases(
            self.llm,
            self.tools,
            self.memory,
            self.identity,
            self.output_schema,
        )

        # Setup MCP server
        self.mcp_server = setup_mcp(self, mcp)

    def _setup_notifier(self, callback=None):
        """Setup v2 notification system."""
        return Notifier(formatter=self.formatter, on_notify=callback or self.on_notify)

    async def stream(self, query: str, user_id: str = "default") -> AsyncIterator[str]:
        """Stream agent execution"""
        # Input validation
        error = validate_query(query)
        if error:
            yield f"{error}\n"
            return

        # Get or create state with persistence support
        state = await get_state(
            user_id,
            query,
            self.depth,
            self.user_states,
            self.config.persist,
        )

        state.add_message("user", query)

        # Load and learn from user input
        if self.memory:
            await self.memory.load()
            await self.memory.remember(query, human=True)

        # Create streaming callback and notification system
        queue: asyncio.Queue[str] = asyncio.Queue()

        async def stream_callback(notification) -> None:
            # Format notification and put in queue
            formatted = self.formatter.format(notification)
            if formatted:
                await queue.put(formatted)

        notifier = self._setup_notifier(callback=stream_callback)

        # Start execution
        from cogency.execution import run_agent

        task = asyncio.create_task(
            run_agent(
                state,
                self.phases["preprocess"],
                self.phases["reason"],
                self.phases["act"],
                self.phases["respond"],
                notifier,
            )
        )

        # Stream notifications
        try:
            while not task.done():
                try:
                    message = await asyncio.wait_for(queue.get(), timeout=0.1)
                    yield message
                except asyncio.TimeoutError:
                    continue

            # Drain remaining
            while not queue.empty():
                yield queue.get_nowait()

        finally:
            result = await task
            self.last_state = result

            # Learn from agent response
            if self.memory and result and hasattr(result, "response"):
                await self.memory.remember(result.response, human=False)

    async def run(self, query: str, user_id: str = "default") -> str:
        """Run agent and return complete response as string (async)"""
        try:
            # Get or create state with persistence support
            state = await get_state(
                user_id,
                query,
                self.depth,
                self.user_states,
                self.config.persist,
            )

            state.add_message("user", query)

            # Load and learn from user input
            if self.memory:
                await self.memory.load()
                await self.memory.remember(query, human=True)

            # Set agent mode - direct, no ceremony
            state.agent_mode = self.mode
            if self.mode != "adapt":
                state.mode = self.mode

            # v2: debug/trace handled via notification system, no callback needed

            # Use simple execution loop with zero ceremony
            from cogency.execution import run_agent

            # Setup notifier
            notifier = self._setup_notifier()

            # Phase instances already have dependencies injected
            await run_agent(
                state,
                self.phases["preprocess"],
                self.phases["reason"],
                self.phases["act"],
                self.phases["respond"],
                notifier,
            )
            self.last_state = state

            # Extract response from state
            response = getattr(state, "response", None)

            # Learn from agent response
            if self.memory and response:
                await self.memory.remember(response, human=False)

            return response or "No response generated"

        except Exception as e:
            # Make errors EXPLICIT
            import traceback

            error_msg = f"Flow execution failed: {e}\n{traceback.format_exc()}"
            print(error_msg)
            raise e

    def traces(self) -> list[dict[str, Any]]:
        """Get detailed execution traces from last run (debug mode only)"""
        if not self.debug:
            return []

        # Return notifications from last execution
        return [
            {"type": n.type, "timestamp": n.timestamp, **n.data}
            for n in self.notifier.notifications
        ]


__all__ = ["Agent", "State"]
