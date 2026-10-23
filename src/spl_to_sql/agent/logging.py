"""Structured logging utilities for agent graph nodes.

Provides helpers to create, finish, and accumulate log entries that
are later rendered as a Rich console tree.
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class AgentLog:
    """A single structured log entry emitted by a graph node.

    Attributes:
        agent_name: Which agent/node emitted the log.
        action: Short action label (e.g. "parse", "llm_fix", "execute").
        status: Status string — "started", "success", "error", "retry",
            "info", "routing", "skipped".
        detail: Human-readable description.
        timestamp: When the log was created.
        duration_ms: How long the action took, if finished.
        children: Nested log entries for sub-steps.
    """

    agent_name: str
    action: str
    status: str
    detail: str
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    duration_ms: float | None = None
    children: list[AgentLog] = field(default_factory=list)

    def add_child(
        self,
        action: str,
        status: str,
        detail: str,
        duration_ms: float | None = None,
    ) -> AgentLog:
        """Add a nested child log entry.

        Args:
            action: Action label for the child.
            status: Status of the child action.
            detail: Human-readable description.
            duration_ms: Duration in milliseconds.

        Returns:
            The created child AgentLog.
        """
        child = AgentLog(
            agent_name=self.agent_name,
            action=action,
            status=status,
            detail=detail,
            duration_ms=duration_ms,
        )
        self.children.append(child)
        return child

    def finish(self, status: str, detail: str, duration_ms: float | None = None) -> None:
        """Update this log entry with a final status.

        Args:
            status: Final status ("success", "error", etc.).
            detail: Final description.
            duration_ms: Total duration in milliseconds.
        """
        self.status = status
        self.detail = detail
        if duration_ms is not None:
            self.duration_ms = duration_ms

    def to_dict(self) -> dict[str, Any]:
        """Serialize to a plain dict for storage in PipelineState.

        Returns:
            Dictionary representation of this log entry.
        """
        return {
            "agent_name": self.agent_name,
            "action": self.action,
            "status": self.status,
            "detail": self.detail,
            "timestamp": self.timestamp.isoformat(),
            "duration_ms": self.duration_ms,
            "children": [c.to_dict() for c in self.children],
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> AgentLog:
        """Deserialize from a plain dict.

        Args:
            data: Dictionary with log entry fields.

        Returns:
            Reconstructed AgentLog instance.
        """
        children = [cls.from_dict(c) for c in data.get("children", [])]
        return cls(
            agent_name=data["agent_name"],
            action=data["action"],
            status=data["status"],
            detail=data["detail"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            duration_ms=data.get("duration_ms"),
            children=children,
        )


def start_log(agent_name: str, detail: str, action: str = "execute") -> AgentLog:
    """Create a new log entry in 'started' status.

    Args:
        agent_name: Name of the agent/node.
        detail: Human-readable description of what's starting.
        action: Action label (default: "execute").

    Returns:
        A new AgentLog in "started" status.
    """
    log_entry = AgentLog(
        agent_name=agent_name,
        action=action,
        status="started",
        detail=detail,
    )
    logger.info("[%s] %s", agent_name, detail)
    return log_entry


def start_timer() -> float:
    """Start a high-resolution timer.

    Returns:
        Current perf_counter value.
    """
    return time.perf_counter()


def elapsed_ms(start: float) -> float:
    """Calculate elapsed milliseconds since a timer start.

    Args:
        start: The value returned by ``start_timer()``.

    Returns:
        Elapsed time in milliseconds.
    """
    return (time.perf_counter() - start) * 1000


def append_log(state_logs: list[dict[str, Any]], log: AgentLog) -> list[dict[str, Any]]:
    """Append a log entry to the state's log list (immutable).

    LangGraph state updates should be immutable — this returns a new
    list rather than mutating in place.

    Args:
        state_logs: Existing list of serialized logs from state.
        log: The new log entry to append.

    Returns:
        New list with the appended log entry.
    """
    return [*state_logs, log.to_dict()]

