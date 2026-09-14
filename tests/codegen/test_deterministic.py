"""Tests for spl_to_sql.codegen.deterministic."""

from __future__ import annotations

import pytest

from spl_to_sql.codegen import deterministic
from spl_to_sql.codegen.dialects.postgres import PostgresDialect
from spl_to_sql.ir.relational_ir.nodes import RelationalQuery, SelectNode


class TestGenerateSQL:
    """Tests for deterministic generate_sql stub."""

    def test_generate_sql_not_implemented(self) -> None:
        """generate_sql() raises NotImplementedError."""
        select = SelectNode(columns=["*"], from_table="events")
        query = RelationalQuery(select=select)
        dialect = PostgresDialect()
        with pytest.raises(NotImplementedError):
            deterministic.generate_sql(query, dialect)
