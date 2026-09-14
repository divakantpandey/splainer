"""Tests for spl_to_sql.ir.transforms.base."""

from __future__ import annotations

import pytest

from spl_to_sql.ir.relational_ir.nodes import RelationalQuery, SelectNode
from spl_to_sql.ir.transforms.base import BaseTransform, apply_transforms


class TestBaseTransform:
    """Tests for BaseTransform abstract class."""

    def test_cannot_instantiate(self) -> None:
        """BaseTransform cannot be instantiated directly."""
        with pytest.raises(TypeError):
            BaseTransform()  # type: ignore[abstract]


class TestApplyTransforms:
    """Tests for apply_transforms stub."""

    def test_apply_transforms_not_implemented(self) -> None:
        """apply_transforms() raises NotImplementedError."""
        select = SelectNode(columns=["*"], from_table="events")
        query = RelationalQuery(select=select)
        with pytest.raises(NotImplementedError):
            apply_transforms(query, [])
