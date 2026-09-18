"""Tests for spl_to_sql.ir.spl_ir.builder."""

from __future__ import annotations

from spl_to_sql.parser import parse
from spl_to_sql.ir.spl_ir import builder

class TestBuildSplIR:
    def test_build_spl_ir(self) -> None:
        tree = parse("search index=main | stats count by sourcetype")
        pipeline = builder.build_spl_ir(tree)
        assert len(pipeline.stages) == 2
        assert pipeline.stages[0].command_name == "search"
        assert pipeline.stages[1].command_name == "stats"
