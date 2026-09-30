"""Exponential backoff retry wrapper.

Wraps SQL execution with tenacity-based exponential backoff and jitter.
Retry attempts are bounded by a configurable maximum.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any, TypeVar

from tenacity import (
    RetryError,
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential_jitter,
)

from spl_to_sql.exceptions import ExecutionError, RetryExhaustedError

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
    """Execute a function with exponential backoff retry."""
    retryer = retry(
        stop=stop_after_attempt(config.max_attempts),
        wait=wait_exponential_jitter(
            initial=config.base_delay_seconds,
            max=config.max_delay_seconds,
            jitter=config.base_delay_seconds if config.jitter else 0,
        ),
        retry=retry_if_exception_type(ExecutionError),
        before_sleep=create_retry_callback(),
        reraise=True,
    )

    try:
        return retryer(func)(*args, **kwargs)
    except RetryError as e:
        last = e.last_attempt.exception() if e.last_attempt else None
        raise RetryExhaustedError(
            message=f"All {config.max_attempts} retry attempts exhausted",
            attempts=config.max_attempts,
            last_error=last if isinstance(last, ExecutionError) else None,
        ) from e


def create_retry_callback(
    on_retry: Callable[[int, Exception], None] | None = None,
) -> Callable[[Any], None]:
    """Create a callback invoked after each failed retry attempt."""

    def _before_sleep(retry_state: Any) -> None:
        attempt = retry_state.attempt_number
        exc = retry_state.outcome.exception() if retry_state.outcome else None
        logger.warning(
            "Retry attempt %d failed: %s. Retrying...",
            attempt,
            exc,
        )
        if on_retry is not None and exc is not None:
            on_retry(attempt, exc)

    return _before_sleep
