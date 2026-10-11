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


from antlr4.error.ErrorListener import ErrorListener
from spl_to_sql.exceptions import ParseError

class SPLErrorCollector(ErrorListener):
    """Collects syntax errors during ANTLR4 parsing.

    Designed to be used as an ANTLR4 error listener. Collects all
    errors rather than failing on the first one, enabling better
    error reporting to the user.

    Attributes:
        errors: List of syntax errors collected during parsing.
    """

    def __init__(self) -> None:
        super().__init__()
        self.errors: list[SyntaxErrorDetail] = []

    def syntaxError(
        self,
        recognizer: Any,
        offendingSymbol: Any,
        line: int,
        column: int,
        msg: str,
        e: Any,
    ) -> None:
        """Called by ANTLR4 when a syntax error is encountered."""
        symbol_text = offendingSymbol.text if offendingSymbol else None
        self.errors.append(
            SyntaxErrorDetail(
                line=line,
                column=column,
                message=msg,
                offending_symbol=symbol_text,
            )
        )

    def raise_if_errors(self) -> None:
        """Raise a ParseError if any syntax errors were collected.

        Raises:
            ParseError: If one or more syntax errors were collected,
                with a formatted multi-line error message.
        """
        if not self.errors:
            return
            
        messages = []
        for err in self.errors:
            symbol_info = f" at '{err.offending_symbol}'" if err.offending_symbol else ""
            messages.append(f"Line {err.line}:{err.column}{symbol_info} - {err.message}")
            
        full_message = "Syntax errors found during parsing:\n" + "\n".join(messages)
        raise ParseError(full_message)
