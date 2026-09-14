"""Tests for spl_to_sql.codegen.llm.grammar_constraint."""

from __future__ import annotations

import pytest

from spl_to_sql.codegen.llm.grammar_constraint import GrammarConstraint


class TestGrammarConstraint:
    """Tests for GrammarConstraint stub methods."""

    def test_constrain_not_implemented(self) -> None:
        """constrain() raises NotImplementedError."""
        gc = GrammarConstraint(dialect="postgres")
        with pytest.raises(NotImplementedError):
            gc.constrain("Generate SQL for counting events")

    def test_validate_output_not_implemented(self) -> None:
        """validate_output() raises NotImplementedError."""
        gc = GrammarConstraint(dialect="postgres")
        with pytest.raises(NotImplementedError):
            gc.validate_output("SELECT COUNT(*) FROM events")
