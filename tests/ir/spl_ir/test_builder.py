"""Tests for spl_to_sql.ir.spl_ir.builder."""

from __future__ import annotations

from typing import Any

import pytest

from spl_to_sql.ir.spl_ir import builder


class TestBuildSplIR:
    """Tests for build_spl_ir stub."""

    def test_build_spl_ir_not_implemented(self, mock_parse_tree: Any) -> None:
        """build_spl_ir() raises NotImplementedError."""
        with pytest.raises(NotImplementedError):
            builder.build_spl_ir(mock_parse_tree)
