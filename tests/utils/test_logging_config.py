"""Tests for spl_to_sql.utils.logging_config."""

from __future__ import annotations

import pytest

from spl_to_sql.utils.logging_config import configure_logging


class TestConfigureLogging:
    """Tests for configure_logging stub."""

    def test_configure_logging(self) -> None:
        from spl_to_sql.utils.logging_config import configure_logging
        configure_logging("DEBUG")
