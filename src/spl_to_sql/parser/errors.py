"""Parser-specific error types and ANTLR4 syntax error collector.

Provides an error listener that integrates with ANTLR4's error reporting
mechanism to collect syntax errors with line/column information.

TODO: Integrate with ANTLR4's BaseErrorListener once generated code exists.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class SyntaxErrorDetail:
    """Structured representation of a single SPL syntax error.

    Attributes:
        line: Line number where the error occurred (1-based).
        column: Column offset where the error occurred (0-based).
        message: Human-readable error description.
        offending_symbol: The token text that caused the error, if available.
    """

    line: int
    column: int
    message: str
    offending_symbol: str | None = None


class SPLErrorCollector:
    """Collects syntax errors during ANTLR4 parsing.

    Designed to be used as an ANTLR4 error listener. Collects all
    errors rather than failing on the first one, enabling better
    error reporting to the user.

    Attributes:
        errors: List of syntax errors collected during parsing.

    TODO: Subclass ANTLR4's BaseErrorListener once generated code exists.
    """

    def __init__(self) -> None:
        self.errors: list[SyntaxErrorDetail] = []

    def syntax_error(
        self,
        recognizer: Any,
        offending_symbol: Any,
        line: int,
        column: int,
        msg: str,
        e: Any,
    ) -> None:
        """Called by ANTLR4 when a syntax error is encountered.

        Args:
            recognizer: The ANTLR4 recognizer (lexer or parser).
            offending_symbol: The offending token.
            line: Line number of the error.
            column: Column offset of the error.
            msg: ANTLR4's error message.
            e: The underlying RecognitionException, if any.

        TODO: Implement error collection logic.
        """
        # TODO: Implement syntax error collection
        raise NotImplementedError("Syntax error collection not yet implemented")

    def raise_if_errors(self) -> None:
        """Raise a ParseError if any syntax errors were collected.

        Raises:
            ParseError: If one or more syntax errors were collected,
                with a formatted multi-line error message.

        TODO: Implement error formatting and raising.
        """
        # TODO: Implement
        raise NotImplementedError("Error raising not yet implemented")
