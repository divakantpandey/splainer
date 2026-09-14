"""Tests for spl_to_sql.codegen.dialects.snowflake."""

from __future__ import annotations

import pytest

from spl_to_sql.codegen.dialects.snowflake import SnowflakeDialect


class TestSnowflakeDialect:
    """Tests for SnowflakeDialect stub methods."""

    def test_name(self) -> None:
        """SnowflakeDialect has the correct name."""
        dialect = SnowflakeDialect()
        assert dialect.name == "snowflake"

    def test_quote_identifier_not_implemented(self) -> None:
        """quote_identifier() raises NotImplementedError."""
        dialect = SnowflakeDialect()
        with pytest.raises(NotImplementedError):
            dialect.quote_identifier("table_name")

    def test_render_limit_not_implemented(self) -> None:
        """render_limit() raises NotImplementedError."""
        dialect = SnowflakeDialect()
        with pytest.raises(NotImplementedError):
            dialect.render_limit(10)

    def test_render_string_literal_not_implemented(self) -> None:
        """render_string_literal() raises NotImplementedError."""
        dialect = SnowflakeDialect()
        with pytest.raises(NotImplementedError):
            dialect.render_string_literal("hello")
