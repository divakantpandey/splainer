"""Agent-based pipeline orchestration for spl-to-sql.

Uses LangGraph to orchestrate the SPL → SQL translation pipeline
with intelligent routing (deterministic vs LLM), automatic error
correction, remote SQL validation, and structured console tree logging.

Usage::

    from spl_to_sql.agent import run_pipeline

    result = run_pipeline("search index=main | stats count by host",
                          dialect="postgres", execute=True)
"""

from __future__ import annotations

from spl_to_sql.agent.state import PipelineResult, PipelineState

__all__ = [
    "PipelineResult",
    "PipelineState",
    "run_pipeline",
]


def run_pipeline(
    query: str,
    dialect: str = "postgres",
    execute: bool = False,
    config_override: SplToSqlConfig | None = None,
) -> PipelineResult:
    """Run the full agent-orchestrated SPL-to-SQL pipeline.

    This is the main public entry point. It builds the LangGraph
    state graph and invokes it with the given query.

    Args:
        query: The SPL query string to translate.
        dialect: Target SQL dialect (default: "postgres").
        execute: Whether to execute the SQL against the remote database.
        config_override: Optional explicit config to use.

    Returns:
        PipelineResult with generated SQL, execution results, and logs.
    """
    from spl_to_sql.agent.graph import build_pipeline_graph
    from spl_to_sql.config import SplToSqlConfig

    config = config_override or SplToSqlConfig.from_env()
    graph = build_pipeline_graph(config)

    initial_state: PipelineState = {
        "original_query": query,
        "dialect": dialect,
        "execute": execute,
        "agent_logs": [],
        "used_llm": False,
        "parse_fix_attempts": 0,
        "validate_fix_attempts": 0,
    }

    final_state = graph.invoke(initial_state)

    return PipelineResult(
        sql=final_state.get("generated_sql", ""),
        execution_result=final_state.get("execution_result", []),
        used_llm=final_state.get("used_llm", False),
        codegen_route=final_state.get("codegen_route", "deterministic"),
        agent_logs=final_state.get("agent_logs", []),
        error=final_state.get("current_error"),
    )

