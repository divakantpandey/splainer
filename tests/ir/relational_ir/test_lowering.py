"""Tests for spl_to_sql.ir.relational_ir.lowering."""

from __future__ import annotations

from spl_to_sql.parser import parse
from spl_to_sql.ir.spl_ir import builder
from spl_to_sql.ir.relational_ir import lowering

class TestLowerToRelational:
    def test_lower(self) -> None:
        tree = parse("search index=main")
        pipeline = builder.build_spl_ir(tree)
        rel_query = lowering.lower_to_relational(pipeline)
        
        assert rel_query.select.from_table == "main"
