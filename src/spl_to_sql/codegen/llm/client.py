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
        """Send a prompt to the LLM and return the generated SQL."""
        import openai
        from spl_to_sql.exceptions import CodegenError
        
        api_key = self.config.api_key.get_secret_value()
        if not api_key:
            # If no API key is provided, check if a custom base URL is used (local models).
            # If so, use a dummy key. Otherwise, raise an error.
            if self.config.base_url:
                api_key = "dummy-local-key"
            else:
                raise CodegenError("LLM API key not configured. Set SPL_TO_SQL_LLM__API_KEY.")
            
        client = openai.OpenAI(
            api_key=api_key,
            base_url=self.config.base_url,
        )
        
        try:
            response = client.chat.completions.create(
                model=self.config.model_name,
                messages=[{"role": "user", "content": prompt}],
                temperature=self.config.temperature,
                max_tokens=self.config.max_tokens,
            )
            
            content = response.choices[0].message.content
            if not content:
                raise CodegenError("LLM returned empty response")
                
            # Extract SQL from markdown code blocks if present
            content = content.strip()
            if content.startswith("```sql"):
                content = content.split("```sql")[1].split("```")[0].strip()
            elif content.startswith("```"):
                content = content.split("```")[1].split("```")[0].strip()
                
            return content
        except Exception as e:
            raise CodegenError(f"LLM API request failed: {e}")

    def generate_corrected_sql(
        self,
        original_sql: str,
        error_message: str,
        dialect: str,
    ) -> str:
        """Request a corrected SQL query after an execution failure."""
        prompt = (
            f"The following {dialect} SQL query failed to execute:\n\n"
            f"```sql\n{original_sql}\n```\n\n"
            f"The database returned this error:\n{error_message}\n\n"
            f"Please provide ONLY the corrected SQL query without any markdown formatting."
        )
        return self.generate_sql(prompt)
