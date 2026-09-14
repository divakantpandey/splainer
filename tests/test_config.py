"""Tests for spl_to_sql.config."""

from __future__ import annotations

from spl_to_sql.config import (
    DatabaseConfig,
    LLMProviderConfig,
    RetryConfig,
    SplToSqlConfig,
    SqlDialect,
)


class TestSqlDialect:
    """Tests for the SqlDialect enum."""

    def test_postgres_value(self) -> None:
        """SqlDialect.POSTGRES has the correct value."""
        assert SqlDialect.POSTGRES == "postgres"

    def test_snowflake_value(self) -> None:
        """SqlDialect.SNOWFLAKE has the correct value."""
        assert SqlDialect.SNOWFLAKE == "snowflake"


class TestLLMProviderConfig:
    """Tests for LLMProviderConfig defaults."""

    def test_defaults(self) -> None:
        """LLMProviderConfig has sensible defaults."""
        config = LLMProviderConfig()
        assert config.model_name == "gpt-4"
        assert config.max_tokens == 2048
        assert config.temperature == 0.0


class TestRetryConfig:
    """Tests for RetryConfig defaults."""

    def test_defaults(self) -> None:
        """RetryConfig has sensible defaults."""
        config = RetryConfig()
        assert config.max_attempts == 3
        assert config.base_delay_seconds == 1.0
        assert config.jitter is True


class TestDatabaseConfig:
    """Tests for DatabaseConfig defaults."""

    def test_defaults(self) -> None:
        """DatabaseConfig has sensible defaults."""
        config = DatabaseConfig()
        assert config.schema_name == "public"
        assert config.timeout_seconds == 30


class TestSplToSqlConfig:
    """Tests for SplToSqlConfig defaults."""

    def test_defaults(self) -> None:
        """SplToSqlConfig has sensible defaults."""
        config = SplToSqlConfig()
        assert config.dialect == SqlDialect.POSTGRES
        assert config.log_level == "INFO"
