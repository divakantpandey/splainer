"""Centralized logging configuration for spl-to-sql.

Provides a single function to configure logging consistently across
all modules. Every module should use ``logging.getLogger(__name__)``
for its logger instance — never ``print()``.

TODO: Implement structured logging (JSON output) option.
TODO: Add log-level override per module.
"""
import logging
import sys

def configure_logging(level: str = "INFO") -> None:
    """Configure the root logger for spl-to-sql.

    Sets up a consistent log format with timestamps, module names,
    and log levels. Output goes to stderr.

    Args:
        level: Log level string (e.g., 'DEBUG', 'INFO', 'WARNING').

    TODO: Implement structured JSON logging option.
    TODO: Add file handler support.
    """
    numeric_level = getattr(logging, level.upper(), logging.INFO)
    
    from rich.logging import RichHandler
    from rich.console import Console

    # Configure Rich logging for detailed, color-coded console output
    logging.basicConfig(
        level=numeric_level,
        format="%(message)s",
        datefmt="[%X]",
        handlers=[
            RichHandler(
                console=Console(stderr=True),
                rich_tracebacks=True,
                show_path=True,
                markup=True,
            )
        ],
        force=True,
    )
