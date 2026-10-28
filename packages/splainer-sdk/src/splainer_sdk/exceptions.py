"""SDK-specific exceptions.

These wrap core library exceptions to provide a stable public API
that doesn't leak internal implementation details.
"""


class SplainerError(Exception):
    """Base exception for all Splainer SDK errors."""


class TranslationError(SplainerError):
    """Raised when SPL-to-SQL translation fails."""


class ParseError(SplainerError):
    """Raised when SPL query parsing fails."""


class CodegenError(SplainerError):
    """Raised when SQL code generation fails."""


class ExecutionError(SplainerError):
    """Raised when SQL execution fails."""


class ConfigurationError(SplainerError):
    """Raised when SDK is misconfigured."""


class APIError(SplainerError):
    """Raised when an API call fails (for future HTTP-mode client)."""

    def __init__(self, message: str, status_code: int | None = None):
        super().__init__(message)
        self.status_code = status_code

