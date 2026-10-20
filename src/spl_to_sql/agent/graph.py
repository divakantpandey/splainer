"""LangGraph state graph builder for the agent pipeline.

Constructs the full ``StateGraph`` with all nodes and conditional
edges, wiring the SPL-to-SQL translation pipeline into a graph
that handles routing, retry loops, and error correction.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from langgraph.graph import END, StateGraph

from spl_to_sql.agent.nodes import create_nodes
from spl_to_sql.agent.routing import (
    route_after_codegen_det,
    route_after_codegen_llm,
    route_after_lowering,
    route_after_parse,
    route_after_parse_fix,
    route_after_validate,
    route_after_validate_fix,
)
from spl_to_sql.agent.state import PipelineState

if TYPE_CHECKING:
    from langgraph.graph.state import CompiledStateGraph

    from spl_to_sql.config import SplToSqlConfig

logger = logging.getLogger(__name__)


def build_pipeline_graph(config: SplToSqlConfig) -> CompiledStateGraph:
    """Build and compile the LangGraph pipeline.

    Creates a ``StateGraph`` with the following structure::

        parse ──┬──▶ ir_build ──▶ lowering ──┬──▶ codegen_det ──┬──▶ validate ──┬──▶ render_output ──▶ END
                │                            │                  │              │
                └──▶ parse_fix ──▶ parse     └──▶ codegen_llm ──┘              └──▶ validate_fix ──▶ validate
                     (retry loop)                 (LLM fallback)                    (retry loop)

    Args:
        config: Application configuration (LLM, DB, retry settings).

    Returns:
        A compiled LangGraph ``CompiledStateGraph`` ready to invoke.
    """
    # Create node functions with config/clients captured in closures
    nodes = create_nodes(config)

    # Build the graph
    graph = StateGraph(PipelineState)

    # ── Add nodes ───────────────────────────────────────────────────
    graph.add_node("parse", nodes["parse_node"])
    graph.add_node("parse_fix", nodes["parse_fix_node"])
    graph.add_node("ir_build", nodes["ir_build_node"])
    graph.add_node("lowering", nodes["lowering_node"])
    graph.add_node("codegen_deterministic", nodes["codegen_deterministic_node"])
    graph.add_node("codegen_llm", nodes["codegen_llm_node"])
    graph.add_node("validate", nodes["validate_node"])
    graph.add_node("validate_fix", nodes["validate_fix_node"])
    graph.add_node("render_output", nodes["render_output_node"])

    # ── Entry point ─────────────────────────────────────────────────
    graph.set_entry_point("parse")

    # ── Edges ───────────────────────────────────────────────────────

    # parse → ir_build (success) or parse_fix (error)
    graph.add_conditional_edges("parse", route_after_parse, {"ir_build": "ir_build", "parse_fix": "parse_fix"})

    # parse_fix → parse (retry) or render_output (max retries)
    graph.add_conditional_edges("parse_fix", route_after_parse_fix, {"parse": "parse", "render_output": "render_output"})

    # ir_build → lowering (always)
    graph.add_edge("ir_build", "lowering")

    # lowering → codegen_deterministic (has relational_ir) or codegen_llm
    graph.add_conditional_edges("lowering", route_after_lowering, {"codegen_deterministic": "codegen_deterministic", "codegen_llm": "codegen_llm"})

    # codegen_deterministic → validate/render_output (success) or codegen_llm
    graph.add_conditional_edges("codegen_deterministic", route_after_codegen_det, {"validate": "validate", "render_output": "render_output", "codegen_llm": "codegen_llm"})

    # codegen_llm → validate (if execute) or render_output
    graph.add_conditional_edges("codegen_llm", route_after_codegen_llm, {"validate": "validate", "render_output": "render_output"})

    # validate → render_output (success) or validate_fix (error)
    graph.add_conditional_edges("validate", route_after_validate, {"render_output": "render_output", "validate_fix": "validate_fix"})

    # validate_fix → validate (retry) or render_output (max retries)
    graph.add_conditional_edges("validate_fix", route_after_validate_fix, {"validate": "validate", "render_output": "render_output"})

    # render_output → END
    graph.add_edge("render_output", END)

    logger.info("Pipeline graph built with %d nodes", len(nodes))
    return graph.compile()

