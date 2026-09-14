"""Tests for spl_to_sql.codegen.llm.client."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from spl_to_sql.codegen.llm.client import LLMClient

if TYPE_CHECKING:
    from spl_to_sql.config import LLMProviderConfig


class TestLLMClient:
    """Tests for LLMClient stub methods."""

    def test_generate_sql_not_implemented(self, llm_config: LLMProviderConfig) -> None:
        """generate_sql() raises NotImplementedError."""
        client = LLMClient(config=llm_config)
        with pytest.raises(NotImplementedError):
            client.generate_sql("SELECT * FROM events")

    def test_generate_corrected_sql_not_implemented(self, llm_config: LLMProviderConfig) -> None:
        """generate_corrected_sql() raises NotImplementedError."""
        client = LLMClient(config=llm_config)
        with pytest.raises(NotImplementedError):
            client.generate_corrected_sql(
                original_sql="SELECT * FORM events",
                error_message="syntax error near FORM",
                dialect="postgres",
            )
