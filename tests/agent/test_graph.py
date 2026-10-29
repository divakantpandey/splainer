"""Tests for LangGraph agent graph building."""

from __future__ import annotations

from langgraph.graph.state import CompiledStateGraph

from spl_to_sql.agent.graph import build_pipeline_graph
from spl_to_sql.config import SplToSqlConfig


def test_build_pipeline_graph():
    """Test that the pipeline graph compiles without raising errors."""
    config = SplToSqlConfig()
    graph = build_pipeline_graph(config)
    assert isinstance(graph, CompiledStateGraph)
