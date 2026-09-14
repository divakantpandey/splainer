"""Tests for spl_to_sql.parser.listener."""

from __future__ import annotations

from typing import Any
from unittest.mock import MagicMock

import pytest

from spl_to_sql.parser.listener import SPLParseTreeListener


class TestSPLParseTreeListener:
    """Tests for SPLParseTreeListener stub methods."""

    def test_walk_not_implemented(self, mock_parse_tree: Any) -> None:
        """walk() raises NotImplementedError."""
        listener = SPLParseTreeListener()
        with pytest.raises(NotImplementedError):
            listener.walk(mock_parse_tree)

    def test_enter_query_not_implemented(self) -> None:
        """enter_query() raises NotImplementedError."""
        listener = SPLParseTreeListener()
        with pytest.raises(NotImplementedError):
            listener.enter_query(MagicMock())

    def test_exit_query_not_implemented(self) -> None:
        """exit_query() raises NotImplementedError."""
        listener = SPLParseTreeListener()
        with pytest.raises(NotImplementedError):
            listener.exit_query(MagicMock())

    def test_enter_command_not_implemented(self) -> None:
        """enter_command() raises NotImplementedError."""
        listener = SPLParseTreeListener()
        with pytest.raises(NotImplementedError):
            listener.enter_command(MagicMock())

    def test_exit_command_not_implemented(self) -> None:
        """exit_command() raises NotImplementedError."""
        listener = SPLParseTreeListener()
        with pytest.raises(NotImplementedError):
            listener.exit_command(MagicMock())

    def test_initial_errors_empty(self) -> None:
        """A new listener should have no errors."""
        listener = SPLParseTreeListener()
        assert listener.errors == []
