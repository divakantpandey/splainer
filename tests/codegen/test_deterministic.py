"""Tests for spl_to_sql.codegen.deterministic."""

from __future__ import annotations

from spl_to_sql.codegen import deterministic
from spl_to_sql.codegen.dialects.postgres import PostgresDialect
from spl_to_sql.ir.relational_ir.nodes import RelationalQuery, SelectNode

class TestGenerateSQL:
    def test_generate_sql(self) -> None:
        select = SelectNode(columns=["*"], from_table="events")
        query = RelationalQuery(select=select)
        dialect = PostgresDialect()
        
        sql = deterministic.generate_sql(query, dialect)
        assert "SELECT *" in sql
        assert "FROM events" in sql
