"""Tests for spl_to_sql.exceptions."""

from __future__ import annotations

from spl_to_sql.exceptions import (
    CodegenError,
    ExecutionError,
    IRLoweringError,
    ParseError,
    RetryExhaustedError,
    SplToSqlError,
)


class TestExceptionHierarchy:
    """Tests for the exception hierarchy."""

    def test_all_exceptions_inherit_from_base(self) -> None:
        """All custom exceptions inherit from SplToSqlError."""
        assert issubclass(ParseError, SplToSqlError)
        assert issubclass(IRLoweringError, SplToSqlError)
        assert issubclass(CodegenError, SplToSqlError)
        assert issubclass(ExecutionError, SplToSqlError)
        assert issubclass(RetryExhaustedError, SplToSqlError)

    def test_base_inherits_from_exception(self) -> None:
        """SplToSqlError inherits from Exception."""
        assert issubclass(SplToSqlError, Exception)

    def test_base_message(self) -> None:
        """SplToSqlError stores a message."""
        err = SplToSqlError("test error")
        assert err.message == "test error"
        assert str(err) == "test error"

    def test_execution_error_attributes(self) -> None:
        """ExecutionError stores SQL and db_error."""
        err = ExecutionError("failed", sql="SELECT 1", db_error="timeout")
        assert err.sql == "SELECT 1"
        assert err.db_error == "timeout"

    def test_retry_exhausted_attributes(self) -> None:
        """RetryExhaustedError stores attempts and last_error."""
        last = ExecutionError("inner")
        err = RetryExhaustedError("exhausted", attempts=3, last_error=last)
        assert err.attempts == 3
        assert err.last_error is last
