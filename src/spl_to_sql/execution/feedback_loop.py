"""Execution failure feedback loop.

On SQL execution failure, feeds the error message back into the
LLM codegen path to request a corrected SQL query. Bounded by
the retry configuration's max attempt count.

This is the "agent API caller until query runs" stage:
1. Execute SQL.
2. If execution fails, extract error info.
3. Send error + original SQL to LLM for correction.
4. Retry with corrected SQL.
5. Repeat until success or max attempts exhausted.

TODO: Implement the feedback loop.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from spl_to_sql.codegen.llm.client import LLMClient
    from spl_to_sql.config import RetryConfig
    from spl_to_sql.execution.runner import SQLRunner

logger = logging.getLogger(__name__)


class FeedbackLoop:
    """Manages the execute → error → LLM correction → retry cycle.

    Coordinates between the SQL runner and the LLM client to
    iteratively correct SQL queries that fail to execute.

    Attributes:
        runner: The SQL execution runner.
        llm_client: The LLM client for generating corrections.
        retry_config: Configuration for retry behavior.

    TODO: Implement the feedback loop.
    TODO: Add execution history tracking for debugging.
    """

    def __init__(
        self,
        runner: SQLRunner,
        llm_client: LLMClient,
        retry_config: RetryConfig,
    ) -> None:
        """Initialize the feedback loop.

        Args:
            runner: SQL execution runner.
            llm_client: LLM client for generating corrections.
            retry_config: Retry/backoff configuration.
        """
        self.runner = runner
        self.llm_client = llm_client
        self.retry_config = retry_config

    def execute_with_feedback(
        self,
        sql: str,
        dialect: str,
    ) -> list[dict[str, Any]]:
        """Execute SQL with automatic error feedback and correction.

        Attempts to execute the SQL query. On failure, sends the error
        to the LLM for correction and retries with the corrected SQL.
        Repeats until success or max_attempts is exhausted.

        Args:
            sql: The initial SQL query to execute.
            dialect: Target SQL dialect name (for LLM correction prompts).

        Returns:
            Query result rows on successful execution.

        Raises:
            RetryExhaustedError: If all correction attempts fail.
            ExecutionError: If a non-retryable error occurs.

        TODO: Implement the feedback loop with bounded retries.
        """
        # TODO: Implement feedback loop
        raise NotImplementedError("Feedback loop not yet implemented")

    def _attempt_correction(
        self,
        sql: str,
        error_message: str,
        dialect: str,
    ) -> str:
        """Request a corrected SQL query from the LLM.

        Args:
            sql: The SQL that failed.
            error_message: The database error message.
            dialect: Target SQL dialect name.

        Returns:
            The corrected SQL query.

        TODO: Implement LLM correction request.
        """
        # TODO: Implement
        raise NotImplementedError("Correction request not yet implemented")
