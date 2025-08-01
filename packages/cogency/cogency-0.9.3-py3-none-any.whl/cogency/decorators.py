"""Agent @phase decorator - Unified composition of resilience + checkpointing + observability."""

from dataclasses import dataclass
from functools import wraps
from typing import Any, Optional

from resilient_result import Retry
from resilient_result import resilient as resilient_decorator

from cogency.observe import counter, histogram, timer
from cogency.robust import checkpoint


@dataclass
class PhaseConfig:
    """Configuration state for phase decorators - injected by Agent at runtime."""

    robust: Optional[Any] = None
    observe: Optional[Any] = None
    persist: Optional[Any] = None


# REMOVED: Global state eliminated - use registry injection


def _checkpoint(name: str, interruptible: bool = True):
    """Context-driven checkpointing wrapper - applies only when task_id exists."""

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Extract state from function arguments
            state = args[0] if args else kwargs.get("state")

            # Apply checkpointing only when task context exists
            if hasattr(state, "context") and hasattr(state.context, "task_id"):
                checkpointed = checkpoint(name, interruptible=interruptible)(func)
                return await checkpointed(*args, **kwargs)

            # No checkpointing overhead for non-task contexts
            return await func(*args, **kwargs)

        return wrapper

    return decorator


def _auto_save(phase_name: str, config: Optional[PhaseConfig] = None):
    """Auto-save state after successful phase completion."""

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Execute the phase
            result = await func(*args, **kwargs)

            # Auto-save only if persistence is configured and phase succeeded
            if config and config.persist and result:
                try:
                    state = args[0] if args else kwargs.get("state")
                    if state:
                        # Handle both Persist config and StatePersistence instance
                        persist_obj = config.persist
                        if hasattr(persist_obj, "save"):
                            # It's a StatePersistence instance
                            await persist_obj.save(state)
                        elif hasattr(persist_obj, "store") and persist_obj.enabled:
                            # It's a Persist config, need to get the StatePersistence instance
                            from cogency.persist.store.base import setup_persistence

                            persistence = setup_persistence(persist_obj)
                            if persistence:
                                await persistence.save(state)
                except Exception:
                    # Don't fail the phase due to persistence issues
                    pass

            return result

        return wrapper

    return decorator


def _observe_metrics(phase_name: str, config: Optional[PhaseConfig] = None):
    """Unified observability wrapper - single timing measurement shared across metrics and notifications."""

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Check if observability is enabled
            if not config or not config.observe:
                return await func(*args, **kwargs)

            # Extract state for context tags
            state = kwargs.get("state") or (args[0] if args else None)
            tags = {
                "phase": phase_name,
                "iteration": str(getattr(state, "iteration", 0)) if state else "0",
                "mode": getattr(state, "mode", "unknown") if state else "unknown",
            }

            # Count phase executions
            counter(f"{phase_name}.executions", 1.0, tags)

            # Start unified timing - metrics collection handles the measurement
            with timer(f"{phase_name}.duration", tags) as phase_timer:
                try:
                    # Inject timing context into kwargs for phase functions to use
                    kwargs["_phase_timer"] = phase_timer

                    result = await func(*args, **kwargs)

                    # Success metrics
                    counter(f"{phase_name}.success", 1.0, tags)

                    # Result size metrics if applicable
                    if result and hasattr(result, "__len__"):
                        histogram(f"{phase_name}.result_size", len(str(result)), tags)

                    return result

                except Exception as e:
                    # Error metrics
                    error_tags = {**tags, "error_type": type(e).__name__}
                    counter(f"{phase_name}.errors", 1.0, error_tags)
                    raise

        return wrapper

    return decorator


def _policy(
    checkpoint_name: str,
    interruptible: bool = True,
    default_retry=None,
    config: Optional[PhaseConfig] = None,
):
    """Universal agent policy factory - composes resilience + checkpointing + persistence."""

    def policy(retry=None, **kwargs):
        retry = retry or default_retry or Retry.api()

        def decorator(func):
            if not config or not config.robust:
                return func

            # 1. Apply resilience
            resilient_func = resilient_decorator(retry=retry)(func)
            # 2. Apply context-driven checkpointing
            checkpointed_func = _checkpoint(checkpoint_name, interruptible)(resilient_func)
            # 3. Apply auto-save after successful completion
            persisted_func = _auto_save(checkpoint_name, config)(checkpointed_func)
            return persisted_func

        return decorator

    return policy


def _observe_policy(phase_name: str, config: Optional[PhaseConfig] = None):
    """Observability policy factory - metrics and telemetry collection."""

    def policy(**kwargs):
        def decorator(func):
            # Apply observability instrumentation
            return _observe_metrics(phase_name, config)(func)

        return decorator

    return policy


def _phase_factory(
    phase_name: str, interruptible: bool, default_retry, config: Optional[PhaseConfig] = None
):
    """Phase decorator factory that combines robust + observe based on config."""

    def phase_decorator(**kwargs):
        def decorator(func):
            # Start with the original function
            result_func = func

            # Apply robust behavior if enabled
            if config and config.robust:
                robust_policy = _policy(phase_name, interruptible, default_retry, config)
                result_func = robust_policy(**kwargs)(result_func)

            # Apply observability if enabled
            if config and config.observe:
                observe_policy = _observe_policy(phase_name, config)
                result_func = observe_policy(**kwargs)(result_func)

            return result_func

        return decorator

    return phase_decorator


def create_phase_decorators(config: Optional[PhaseConfig] = None):
    """Create phase decorators with injected config - no global state."""

    class _PhaseDecorators:
        """Unified @phase decorator with beautiful IDE autocomplete."""

        reason = staticmethod(_phase_factory("reasoning", True, Retry.api(), config))
        act = staticmethod(_phase_factory("tool_execution", True, Retry.db(), config))
        prepare = staticmethod(
            _phase_factory("preparing", False, Retry(attempts=2, timeout=10.0), config)
        )
        respond = staticmethod(
            _phase_factory("response", False, Retry(attempts=2, timeout=15.0), config)
        )
        generic = staticmethod(_phase_factory("generic", True, None, config))

    return _PhaseDecorators()


# Backward compatibility - phase decorators with no config
phase = create_phase_decorators()


# DEPRECATED: Remove in v1.0.0 - use create_phase_decorators() with config injection
def configure(robust=None, observe=None, persistence=None):
    """DEPRECATED: Global configuration removed. Use create_phase_decorators(config) instead."""
    raise DeprecationWarning(
        "Global decorators.configure() removed. Use create_phase_decorators(PhaseConfig(...)) instead."
    )


def elapsed(**kwargs) -> float:
    """Get current phase duration from injected timer context."""
    timer_context = kwargs.get("_phase_timer")
    return timer_context.current_elapsed if timer_context else 0.0


__all__ = [
    "phase",
    "create_phase_decorators",
    "PhaseConfig",
    "configure",  # DEPRECATED
    "elapsed",
]
