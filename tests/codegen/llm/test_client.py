"""Tests for spl_to_sql.codegen.llm.client."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from spl_to_sql.codegen.llm.client import LLMClient

if TYPE_CHECKING:
    from spl_to_sql.config import LLMProviderConfig


class TestLLMClient:
    """Tests for LLMClient stub methods."""

    def test_generate_sql(self, llm_config: LLMProviderConfig, mocker) -> None:
        client = LLMClient(config=llm_config)
        mock_openai = mocker.patch("openai.OpenAI")
        mock_openai.return_value.chat.completions.create.return_value.choices[0].message.content = "```sql\nSELECT * FROM events;\n```"
        
        # Override config so api_key is present
        from pydantic import SecretStr
        client.config.api_key = SecretStr("test-key")
        
        result = client.generate_sql("some prompt")
        assert result == "SELECT * FROM events;"

    def test_generate_corrected_sql(self, llm_config: LLMProviderConfig, mocker) -> None:
        client = LLMClient(config=llm_config)
        mock_openai = mocker.patch("openai.OpenAI")
        mock_openai.return_value.chat.completions.create.return_value.choices[0].message.content = "SELECT * FROM events;"
        
        from pydantic import SecretStr
        client.config.api_key = SecretStr("test-key")
        
        result = client.generate_corrected_sql(
            original_sql="SELECT * FORM events",
            error_message="syntax error near FORM",
            dialect="postgres",
        )
        assert result == "SELECT * FROM events;"
