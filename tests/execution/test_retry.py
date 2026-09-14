"""Tests for spl_to_sql.execution.retry."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from spl_to_sql.execution.retry import create_retry_callback, with_retry

if TYPE_CHECKING:
    from spl_to_sql.config import RetryConfig


class TestWithRetry:
    """Tests for with_retry stub."""

    def test_with_retry_not_implemented(self, retry_config: RetryConfig) -> None:
        """with_retry() raises NotImplementedError."""
        with pytest.raises(NotImplementedError):
            with_retry(lambda: None, retry_config)


class TestCreateRetryCallback:
    """Tests for create_retry_callback stub."""

    def test_create_retry_callback_not_implemented(self) -> None:
        """create_retry_callback() raises NotImplementedError."""
        with pytest.raises(NotImplementedError):
            create_retry_callback()
