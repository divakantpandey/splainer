"""Tests for spl_to_sql.ir.relational_ir.lowering."""

from __future__ import annotations

import pytest

from spl_to_sql.ir.relational_ir import lowering
from spl_to_sql.ir.spl_ir.nodes import (
    PipelineStage,
    SearchCommand,
    SPLPipeline,
)


class TestLowerToRelational:
    """Tests for lower_to_relational stub."""

    def test_lower_not_implemented(self) -> None:
        """lower_to_relational() raises NotImplementedError."""
        cmd = SearchCommand(search_expression="index=main")
        stage = PipelineStage(command_name="search", command=cmd)
        pipeline = SPLPipeline(stages=[stage])
        with pytest.raises(NotImplementedError):
            lowering.lower_to_relational(pipeline)
