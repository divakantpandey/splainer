"""Tests for spl_to_sql.codegen.dialects.postgres."""

from __future__ import annotations

import pytest

from spl_to_sql.codegen.dialects.postgres import PostgresDialect


class TestPostgresDialect:
    """Tests for PostgresDialect stub methods."""

    def test_name(self) -> None:
        """PostgresDialect has the correct name."""
        dialect = PostgresDialect()
        assert dialect.name == "postgres"

    def test_quote_identifier_not_implemented(self) -> None:
        """quote_identifier() raises NotImplementedError."""
        dialect = PostgresDialect()
        with pytest.raises(NotImplementedError):
            dialect.quote_identifier("table_name")

    def test_render_limit_not_implemented(self) -> None:
        """render_limit() raises NotImplementedError."""
        dialect = PostgresDialect()
        with pytest.raises(NotImplementedError):
            dialect.render_limit(10)

    def test_render_string_literal_not_implemented(self) -> None:
        """render_string_literal() raises NotImplementedError."""
        dialect = PostgresDialect()
        with pytest.raises(NotImplementedError):
            dialect.render_string_literal("hello")
