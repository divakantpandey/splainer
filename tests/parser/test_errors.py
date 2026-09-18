"""Tests for spl_to_sql.parser.errors."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from spl_to_sql.parser.errors import SPLErrorCollector, SyntaxErrorDetail


class TestSyntaxErrorDetail:
    """Tests for SyntaxErrorDetail dataclass."""

    def test_creation(self) -> None:
        """SyntaxErrorDetail can be created with required fields."""
        detail = SyntaxErrorDetail(line=1, column=5, message="unexpected token")
        assert detail.line == 1
        assert detail.column == 5
        assert detail.message == "unexpected token"
        assert detail.offending_symbol is None

    def test_frozen(self) -> None:
        """SyntaxErrorDetail is immutable."""
        detail = SyntaxErrorDetail(line=1, column=0, message="error")
        with pytest.raises(AttributeError):
            detail.line = 2  # type: ignore[misc]


class TestSPLErrorCollector:
    """Tests for SPLErrorCollector stub methods."""

    def test_initial_errors_empty(self) -> None:
        """A new collector should have no errors."""
        collector = SPLErrorCollector()
        assert collector.errors == []

    def test_syntax_error(self) -> None:
        collector = SPLErrorCollector()
        mock_symbol = MagicMock()
        mock_symbol.text = "bad"
        collector.syntaxError(
            recognizer=MagicMock(),
            offendingSymbol=mock_symbol,
            line=1,
            column=0,
            msg="test error",
            e=None,
        )
        assert len(collector.errors) == 1

    def test_raise_if_errors(self) -> None:
        from spl_to_sql.exceptions import ParseError
        collector = SPLErrorCollector()
        collector.errors.append(SyntaxErrorDetail(line=1, column=1, message="test"))
        with pytest.raises(ParseError):
            collector.raise_if_errors()
