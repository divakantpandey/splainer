"""LLM provider client wrapper.

Abstracts the LLM API interaction behind a simple interface.
Supports configurable providers (OpenAI, Anthropic, etc.) via
the LLMProviderConfig in config.py.

TODO: Implement actual LLM API calls.
TODO: Add response parsing and validation.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from spl_to_sql.config import LLMProviderConfig

logger = logging.getLogger(__name__)


class LLMClient:
    """Client wrapper for LLM API interactions.

    Provides a simple interface for sending prompts to an LLM and
    receiving SQL text responses. Handles API authentication,
    request formatting, and response extraction.

    Attributes:
        config: The LLM provider configuration.

    TODO: Implement actual API calls.
    TODO: Add streaming support.
    TODO: Add token usage tracking.
    """

    def __init__(self, config: LLMProviderConfig) -> None:
        """Initialize the LLM client.

        Args:
            config: LLM provider configuration with API key, model, etc.
        """
        self.config = config

    def generate_sql(self, prompt: str) -> str:
        """Send a prompt to the LLM and return the generated SQL.

        Args:
            prompt: The formatted prompt string.

        Returns:
            The generated SQL query string.

        Raises:
            CodegenError: If the LLM request fails or returns invalid output.

        TODO: Implement LLM API call.
        TODO: Add response validation (is the output valid SQL?).
        """
        # TODO: Implement LLM API call
        raise NotImplementedError("LLM SQL generation not yet implemented")

    def generate_corrected_sql(
        self,
        original_sql: str,
        error_message: str,
        dialect: str,
    ) -> str:
        """Request a corrected SQL query after an execution failure.

        Args:
            original_sql: The SQL that failed to execute.
            error_message: The database error message.
            dialect: Target SQL dialect name.

        Returns:
            The corrected SQL query string.

        Raises:
            CodegenError: If the LLM request fails.

        TODO: Implement error correction flow.
        """
        # TODO: Implement LLM error correction
        raise NotImplementedError("LLM error correction not yet implemented")
