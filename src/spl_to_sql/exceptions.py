"""Exception hierarchy for spl-to-sql.

All exceptions raised by spl-to-sql modules inherit from SplToSqlError.
Each pipeline stage has a dedicated exception subclass. Bare exceptions
should never be raised — always use this hierarchy.

TODO: Add more specific exception subclasses as stages are implemented.
"""


class SplToSqlError(Exception):
    """Base exception for all spl-to-sql errors.

    Attributes:
        message: Human-readable error description.
    """

    def __init__(self, message: str = "") -> None:
        self.message = message
        super().__init__(self.message)


class ParseError(SplToSqlError):
    """Raised when SPL query parsing fails.

    This covers lexer errors, syntax errors, and any failure in the
    ANTLR4 parse tree construction stage.

    TODO: Include line/column information from ANTLR error listener.
    """


class IRLoweringError(SplToSqlError):
    """Raised when IR transformation fails.

    Covers failures in both SPL IR building (parse tree → spl_ir) and
    lowering (spl_ir → relational_ir).

    TODO: Split into BuildError and LoweringError if needed.
    """


class CodegenError(SplToSqlError):
    """Raised when SQL code generation fails.

    Covers both deterministic codegen failures and LLM codegen failures.

    TODO: Add subclasses for deterministic vs LLM failures.
    """


class ExecutionError(SplToSqlError):
    """Raised when SQL execution against the target database fails.

    Attributes:
        sql: The SQL statement that failed.
        db_error: The underlying database error message.

    TODO: Capture structured error info from DB drivers.
    """

    def __init__(
        self,
        message: str = "",
        *,
        sql: str = "",
        db_error: str = "",
    ) -> None:
        self.sql = sql
        self.db_error = db_error
        super().__init__(message)


class RetryExhaustedError(SplToSqlError):
    """Raised when all retry attempts have been exhausted.

    Attributes:
        attempts: Number of attempts made before giving up.
        last_error: The last error encountered.

    TODO: Include full attempt history for debugging.
    """

    def __init__(
        self,
        message: str = "",
        *,
        attempts: int = 0,
        last_error: SplToSqlError | None = None,
    ) -> None:
        self.attempts = attempts
        self.last_error = last_error
        super().__init__(message)
