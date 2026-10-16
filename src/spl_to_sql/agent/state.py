"""Pipeline state and result types for the agent graph.

Defines the shared ``PipelineState`` TypedDict that flows through every
LangGraph node, and the ``PipelineResult`` returned to callers.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, TypedDict


class PipelineState(TypedDict, total=False):
    """Shared state flowing through all LangGraph nodes.

    Every node reads from and writes to this dict. Fields are populated
    incrementally as the pipeline progresses.
    """

    # ── Inputs ──────────────────────────────────────────────────────
    original_query: str
    dialect: str
    execute: bool

    # ── Pipeline artifacts (populated by nodes) ─────────────────────
    parse_tree: Any  # ANTLR4 parse tree context
    spl_ir: Any  # SPLPipeline
    relational_ir: Any  # RelationalQuery or None
    generated_sql: str  # Final SQL string
    execution_result: list[dict[str, Any]]  # Rows from remote DB

    # ── Agent metadata ──────────────────────────────────────────────
    used_llm: bool  # Whether LLM was used anywhere
    codegen_route: str  # "deterministic" or "llm"
    parse_fix_attempts: int  # Counter for parse fix retries
    validate_fix_attempts: int  # Counter for validation fix retries
    current_error: str  # Error message for fix nodes
    current_error_sql: str  # SQL that failed (for validation fix)

    # ── Logging ─────────────────────────────────────────────────────
    agent_logs: list[dict[str, Any]]  # Accumulated log entries


@dataclass
class PipelineResult:
    """Final result returned from the agent pipeline.

    Attributes:
        sql: The generated (and possibly corrected) SQL string.
        execution_result: Query results if execution was requested.
        used_llm: Whether the LLM was involved at any point.
        codegen_route: Which codegen path was used.
        agent_logs: Full structured logs for console tree rendering.
        error: Final error if the pipeline did not fully succeed.
    """

    sql: str = ""
    execution_result: list[dict[str, Any]] = field(default_factory=list)
    used_llm: bool = False
    codegen_route: str = "deterministic"
    agent_logs: list[dict[str, Any]] = field(default_factory=list)
    error: str | None = None

