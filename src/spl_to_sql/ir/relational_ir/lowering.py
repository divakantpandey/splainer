"""SPL IR → Relational IR lowering.

Transforms the SPL-shaped IR into a relational-algebra-shaped IR
that can be directly consumed by the codegen stage. This is where
SPL-specific semantics (piped commands, implicit search) are mapped
to relational concepts (SELECT, WHERE, GROUP BY).

TODO: Implement lowering rules for each SPL command type.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from spl_to_sql.ir.relational_ir.nodes import RelationalQuery
    from spl_to_sql.ir.spl_ir.nodes import SPLPipeline

logger = logging.getLogger(__name__)


def lower_to_relational(spl_pipeline: SPLPipeline) -> RelationalQuery:
    """Lower an SPL IR pipeline to a Relational IR query.

    This is the main entry point for Stage 3 of the pipeline.
    Takes the SPL-shaped IR and transforms it into a relational-
    algebra-shaped IR suitable for SQL code generation.

    Args:
        spl_pipeline: The SPL IR pipeline to lower.

    Returns:
        A RelationalQuery representing the equivalent SQL query.

    Raises:
        IRLoweringError: If the SPL pipeline contains constructs
            that cannot be mapped to relational operations.

    TODO: Implement lowering rules per SPL command type:
        - search → SELECT ... WHERE ...
        - stats → SELECT ... GROUP BY ...
        - sort → ORDER BY ...
        - eval → computed columns in SELECT
    """
    # TODO: Implement SPL IR → Relational IR lowering
    raise NotImplementedError("IR lowering not yet implemented")


def _lower_search(search_expression: str, index: str | None) -> str:
    """Lower an SPL search expression to a SQL WHERE clause fragment.

    Args:
        search_expression: The SPL search filter text.
        index: Optional index name to map to a table.

    Returns:
        A SQL WHERE clause fragment string.

    TODO: Implement search expression translation.
    """
    # TODO: Implement
    raise NotImplementedError


def _lower_stats(
    aggregations: list[str],
    group_by: list[str],
) -> tuple[list[str], list[str]]:
    """Lower SPL stats aggregations to SQL SELECT columns and GROUP BY.

    Args:
        aggregations: SPL aggregation expressions.
        group_by: SPL group-by field names.

    Returns:
        Tuple of (select_columns, group_by_columns) for the SQL query.

    TODO: Implement aggregation function mapping.
    """
    # TODO: Implement
    raise NotImplementedError
