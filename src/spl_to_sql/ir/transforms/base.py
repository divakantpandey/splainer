"""Base class for IR-to-IR optimization transforms.

# NOTE: This module is OPTIONAL for v0. See transforms/__init__.py.

Provides an abstract base for implementing optimization passes that
operate on the Relational IR. Each transform takes a RelationalQuery
and returns an optimized RelationalQuery.

TODO: Implement concrete transforms (predicate pushdown, constant folding).
"""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from spl_to_sql.ir.relational_ir.nodes import RelationalQuery

logger = logging.getLogger(__name__)


class BaseTransform(ABC):
    """Abstract base class for IR optimization transforms.

    Subclasses implement specific optimization passes that rewrite
    the Relational IR for better SQL output.

    TODO: Implement concrete transform subclasses.
    """

    @abstractmethod
    def apply(self, query: RelationalQuery) -> RelationalQuery:
        """Apply this optimization transform to a relational query.

        Args:
            query: The input Relational IR query.

        Returns:
            The optimized Relational IR query.

        TODO: Implement in concrete subclasses.
        """
        ...

    @property
    @abstractmethod
    def name(self) -> str:
        """Human-readable name of this transform, for logging.

        Returns:
            The transform name.
        """
        ...


def apply_transforms(
    query: RelationalQuery,
    transforms: list[BaseTransform],
) -> RelationalQuery:
    """Apply a sequence of optimization transforms to a query.

    Args:
        query: The input Relational IR query.
        transforms: Ordered list of transforms to apply.

    Returns:
        The optimized Relational IR query after all transforms.

    TODO: Add transform logging and metrics.
    """
    # TODO: Implement transform pipeline
    raise NotImplementedError("Transform pipeline not yet implemented")
