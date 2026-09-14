"""Exponential backoff retry wrapper.

Wraps SQL execution with tenacity-based exponential backoff and jitter.
Retry attempts are bounded by a configurable maximum, and each failed
attempt's error is captured for the feedback loop.

Backoff strategy:
- Exponential with configurable base delay and max delay cap.
- Random jitter to avoid thundering herd.
- Max attempt ceiling (default: 3, configurable via RetryConfig).
- Each attempt captures the execution error for feedback.

TODO: Implement actual retry logic using tenacity.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any, TypeVar

if TYPE_CHECKING:
    from collections.abc import Callable

    from spl_to_sql.config import RetryConfig

logger = logging.getLogger(__name__)

T = TypeVar("T")


def with_retry(
    func: Callable[..., T],
    config: RetryConfig,
    *args: Any,
    **kwargs: Any,
) -> T:
    """Execute a function with exponential backoff retry.

    Wraps the given function with tenacity-based retry logic.
    On each failure, captures the error for potential feedback
    to the LLM correction loop.

    Backoff behavior:
    - Base delay: config.base_delay_seconds
    - Max delay: config.max_delay_seconds
    - Jitter: enabled if config.jitter is True
    - Max attempts: config.max_attempts

    Args:
        func: The function to execute with retry.
        config: Retry configuration (delays, max attempts, jitter).
        *args: Positional arguments passed to func.
        **kwargs: Keyword arguments passed to func.

    Returns:
        The return value of func on success.

    Raises:
        RetryExhaustedError: If all retry attempts fail.

    TODO: Implement using tenacity decorators.
    """
    # TODO: Implement tenacity-based retry
    raise NotImplementedError("Retry logic not yet implemented")


def create_retry_callback(
    on_retry: Callable[[int, Exception], None] | None = None,
) -> Callable[[Any], None]:
    """Create a callback invoked after each failed retry attempt.

    Args:
        on_retry: Optional callback receiving (attempt_number, exception).

    Returns:
        A tenacity-compatible retry callback.

    TODO: Implement callback creation.
    """
    # TODO: Implement
    raise NotImplementedError("Retry callback not yet implemented")
