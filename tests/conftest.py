"""Shared test fixtures for spl-to-sql.

Provides placeholder fixtures for use across all test modules.
Fixtures return dummy data for now — replace with realistic test
data as stages are implemented.

TODO: Add realistic SPL query fixtures from real Splunk usage.
TODO: Add mock database result fixtures.
"""

from __future__ import annotations

from typing import Any
from unittest.mock import MagicMock

import pytest

from spl_to_sql.config import (
    DatabaseConfig,
    LLMProviderConfig,
    RetryConfig,
    SplToSqlConfig,
)

# --- Sample SPL query strings ---


@pytest.fixture()
def simple_spl_query() -> str:
    """A simple SPL search query."""
    return "search index=main sourcetype=syslog | stats count by host"


@pytest.fixture()
def complex_spl_query() -> str:
    """A more complex SPL query with multiple pipeline stages."""
    return (
        "search index=web_logs status=500 "
        "| eval response_time_ms=response_time*1000 "
        "| stats avg(response_time_ms) as avg_rt, count by uri_path "
        "| sort -count "
    )


@pytest.fixture()
def minimal_spl_query() -> str:
    """The simplest possible SPL query."""
    return "search index=main"


# --- Configuration fixtures ---


@pytest.fixture()
def llm_config() -> LLMProviderConfig:
    """LLM provider configuration for testing."""
    return LLMProviderConfig(
        model_name="test-model",
        max_tokens=100,
        temperature=0.0,
    )


@pytest.fixture()
def retry_config() -> RetryConfig:
    """Retry configuration for testing."""
    return RetryConfig(
        max_attempts=2,
        base_delay_seconds=0.1,
        max_delay_seconds=1.0,
        jitter=False,
    )


@pytest.fixture()
def db_config() -> DatabaseConfig:
    """Database configuration for testing."""
    return DatabaseConfig(
        schema_name="test_schema",
        timeout_seconds=5,
    )


@pytest.fixture()
def app_config() -> SplToSqlConfig:
    """Top-level application configuration for testing."""
    return SplToSqlConfig(log_level="DEBUG")


# --- Mock fixtures ---


@pytest.fixture()
def mock_llm_client() -> MagicMock:
    """Mock LLM client that returns a placeholder SQL query."""
    client = MagicMock()
    client.generate_sql.return_value = "SELECT * FROM placeholder"
    client.generate_corrected_sql.return_value = "SELECT 1"
    return client


@pytest.fixture()
def mock_db_connection() -> MagicMock:
    """Mock database connection that returns dummy results."""
    conn = MagicMock()
    conn.execute.return_value = [{"col1": "val1", "col2": 42}]
    return conn


@pytest.fixture()
def mock_parse_tree() -> Any:
    """Mock ANTLR4 parse tree (placeholder)."""
    return MagicMock(name="MockParseTree")


@pytest.fixture()
def sample_sql_result() -> list[dict[str, Any]]:
    """Sample SQL query result rows."""
    return [
        {"host": "server1", "count": 150},
        {"host": "server2", "count": 89},
        {"host": "server3", "count": 42},
    ]
