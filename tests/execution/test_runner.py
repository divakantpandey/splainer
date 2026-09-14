"""Tests for spl_to_sql.execution.runner."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from spl_to_sql.execution.runner import SQLRunner

if TYPE_CHECKING:
    from spl_to_sql.config import DatabaseConfig


class TestSQLRunner:
    """Tests for SQLRunner stub methods."""

    def test_execute_not_implemented(self, db_config: DatabaseConfig) -> None:
        """execute() raises NotImplementedError."""
        runner = SQLRunner(config=db_config)
        with pytest.raises(NotImplementedError):
            runner.execute("SELECT 1")

    def test_validate_connection_not_implemented(self, db_config: DatabaseConfig) -> None:
        """validate_connection() raises NotImplementedError."""
        runner = SQLRunner(config=db_config)
        with pytest.raises(NotImplementedError):
            runner.validate_connection()
