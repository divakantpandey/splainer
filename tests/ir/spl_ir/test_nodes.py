"""Tests for spl_to_sql.ir.spl_ir.nodes."""

from __future__ import annotations

from spl_to_sql.ir.spl_ir.nodes import (
    FieldRef,
    PipelineStage,
    SearchCommand,
    SortCommand,
    SPLNode,
    SPLPipeline,
    StatsCommand,
    Literal
)

class TestSPLNode:
    def test_default_source_text(self) -> None:
        node = SPLNode()
        assert node.source_text == ""

class TestSearchCommand:
    def test_creation_minimal(self) -> None:
        cmd = SearchCommand(expression=None)
        assert cmd.expression is None
        assert cmd.index is None
        assert cmd.sourcetype is None

    def test_creation_full(self) -> None:
        cmd = SearchCommand(
            expression=Literal(value=True),
            index="main",
            sourcetype="syslog",
        )
        assert cmd.index == "main"
        assert cmd.sourcetype == "syslog"

class TestStatsCommand:
    def test_creation(self) -> None:
        cmd = StatsCommand(
            aggregations=[],
            group_by=[],
        )
        assert cmd.aggregations == []
        assert cmd.group_by == []

class TestSortCommand:
    def test_creation(self) -> None:
        cmd = SortCommand(fields=["-count", "host"])
        assert cmd.fields == ["-count", "host"]

class TestPipelineStage:
    def test_creation(self) -> None:
        cmd = SearchCommand(expression=None)
        stage = PipelineStage(command_name="search", command=cmd)
        assert stage.command_name == "search"

class TestSPLPipeline:
    def test_creation(self) -> None:
        cmd = SearchCommand(expression=None)
        stage = PipelineStage(command_name="search", command=cmd)
        pipeline = SPLPipeline(stages=[stage])
        assert len(pipeline.stages) == 1

    def test_empty_pipeline(self) -> None:
        pipeline = SPLPipeline(stages=[])
        assert pipeline.stages == []
