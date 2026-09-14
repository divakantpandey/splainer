"""Tests for spl_to_sql.execution.feedback_loop."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from spl_to_sql.codegen.llm.client import LLMClient
from spl_to_sql.execution.feedback_loop import FeedbackLoop
from spl_to_sql.execution.runner import SQLRunner

if TYPE_CHECKING:
    from spl_to_sql.config import DatabaseConfig, LLMProviderConfig, RetryConfig


class TestFeedbackLoop:
    """Tests for FeedbackLoop stub methods."""

    def test_execute_with_feedback_not_implemented(
        self,
        db_config: DatabaseConfig,
        llm_config: LLMProviderConfig,
        retry_config: RetryConfig,
    ) -> None:
        """execute_with_feedback() raises NotImplementedError."""
        runner = SQLRunner(config=db_config)
        llm_client = LLMClient(config=llm_config)
        loop = FeedbackLoop(
            runner=runner,
            llm_client=llm_client,
            retry_config=retry_config,
        )
        with pytest.raises(NotImplementedError):
            loop.execute_with_feedback(
                sql="SELECT * FROM events",
                dialect="postgres",
            )


class TestFeedbackLoopIntegration:
    """Integration tests for the feedback loop (requires live services)."""

    @pytest.mark.integration()
    def test_full_feedback_cycle(self) -> None:
        """Test the full execute → error → correct → retry cycle.

        Requires a live database and LLM API connection.
        Run with: uv run pytest -m integration

        TODO: Implement once services are available.
        """
        pytest.skip("Integration test — requires live DB and LLM API")
