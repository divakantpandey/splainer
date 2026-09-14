"""Tests for spl_to_sql.ir.spl_ir.nodes."""

from __future__ import annotations

from spl_to_sql.ir.spl_ir.nodes import (
    EvalExpression,
    FieldReference,
    PipelineStage,
    SearchCommand,
    SortCommand,
    SPLNode,
    SPLPipeline,
    StatsCommand,
)


class TestSPLNode:
    """Tests for SPLNode base model."""

    def test_default_source_text(self) -> None:
        """SPLNode has empty source_text by default."""
        node = SPLNode()
        assert node.source_text == ""


class TestFieldReference:
    """Tests for FieldReference model."""

    def test_creation(self) -> None:
        """FieldReference can be created with a field name."""
        ref = FieldReference(field_name="host")
        assert ref.field_name == "host"


class TestEvalExpression:
    """Tests for EvalExpression model."""

    def test_creation(self) -> None:
        """EvalExpression can be created with target and expression."""
        expr = EvalExpression(
            target_field="new_field",
            expression_text="old_field * 2",
        )
        assert expr.target_field == "new_field"
        assert expr.expression_text == "old_field * 2"


class TestSearchCommand:
    """Tests for SearchCommand model."""

    def test_creation_minimal(self) -> None:
        """SearchCommand can be created with just search_expression."""
        cmd = SearchCommand(search_expression="error")
        assert cmd.search_expression == "error"
        assert cmd.index is None
        assert cmd.sourcetype is None

    def test_creation_full(self) -> None:
        """SearchCommand can be created with all fields."""
        cmd = SearchCommand(
            search_expression="error",
            index="main",
            sourcetype="syslog",
        )
        assert cmd.index == "main"
        assert cmd.sourcetype == "syslog"


class TestStatsCommand:
    """Tests for StatsCommand model."""

    def test_creation(self) -> None:
        """StatsCommand can be created with aggregations."""
        cmd = StatsCommand(
            aggregations=["count", "avg(bytes)"],
            group_by_fields=["host"],
        )
        assert cmd.aggregations == ["count", "avg(bytes)"]
        assert cmd.group_by_fields == ["host"]


class TestSortCommand:
    """Tests for SortCommand model."""

    def test_creation(self) -> None:
        """SortCommand can be created with field list."""
        cmd = SortCommand(fields=["-count", "host"])
        assert cmd.fields == ["-count", "host"]


class TestPipelineStage:
    """Tests for PipelineStage model."""

    def test_creation(self) -> None:
        """PipelineStage wraps a command."""
        cmd = SearchCommand(search_expression="index=main")
        stage = PipelineStage(command_name="search", command=cmd)
        assert stage.command_name == "search"


class TestSPLPipeline:
    """Tests for SPLPipeline model."""

    def test_creation(self) -> None:
        """SPLPipeline wraps a list of stages."""
        cmd = SearchCommand(search_expression="index=main")
        stage = PipelineStage(command_name="search", command=cmd)
        pipeline = SPLPipeline(stages=[stage])
        assert len(pipeline.stages) == 1

    def test_empty_pipeline(self) -> None:
        """SPLPipeline can be created with no stages."""
        pipeline = SPLPipeline(stages=[])
        assert pipeline.stages == []
