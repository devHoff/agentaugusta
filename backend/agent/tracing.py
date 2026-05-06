"""
Langfuse tracing helpers for agent workflows.

The OpenAI wrapper captures individual generations automatically. These helpers
add higher-level agent spans so multi-call workflows are grouped by client/event.
"""
from contextlib import contextmanager
import os
from typing import Any, Iterator, Optional

try:
    from langfuse import get_client, propagate_attributes
except Exception:  # pragma: no cover - keeps local dev usable before deps/env are set
    get_client = None
    propagate_attributes = None


@contextmanager
def trace_agent_event(
    name: str,
    client_id: str,
    event_type: str,
    input_data: Optional[dict[str, Any]] = None,
    metadata: Optional[dict[str, Any]] = None,
) -> Iterator[Any]:
    """Create a Langfuse agent span and propagate filterable attributes."""
    if get_client is None or propagate_attributes is None:
        yield None
        return

    tags = ["pm-agent", event_type]
    span_metadata = {
        "client_id": client_id,
        "event_type": event_type,
        **(metadata or {}),
    }

    try:
        langfuse = get_client()
        span_context = langfuse.start_as_current_observation(as_type="agent", name=name)
    except Exception:
        yield None
        return

    with span_context as span:
        span.update(input=input_data or {}, metadata=span_metadata)
        with propagate_attributes(
            session_id=f"client:{client_id}",
            tags=tags,
            metadata=span_metadata,
        ):
            yield span


def update_trace_output(span: Any, output: Optional[dict[str, Any]]) -> None:
    """Set concise workflow output without exposing full generated documents."""
    if span is not None:
        span.update(output=output or {})


def flush_traces() -> None:
    """Flush queued Langfuse events on application shutdown."""
    if get_client is not None:
        try:
            get_client().flush()
        except Exception:
            pass


def get_tracing_status() -> dict[str, Any]:
    """Return non-sensitive Langfuse configuration status."""
    return {
        "enabled": os.environ.get("LANGFUSE_TRACING_ENABLED", "true").lower() != "false",
        "has_public_key": bool(os.environ.get("LANGFUSE_PUBLIC_KEY")),
        "has_secret_key": bool(os.environ.get("LANGFUSE_SECRET_KEY")),
        "base_url": os.environ.get("LANGFUSE_BASE_URL") or os.environ.get("LANGFUSE_HOST"),
        "sdk_installed": get_client is not None,
    }
