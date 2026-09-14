"""Pydantic models for Relational IR nodes.

These models represent the SQL-shaped intermediate representation.
Each node type corresponds to a relational algebra concept.

TODO: Add more node types as SQL constructs are needed.
TODO: Add validation rules to pydantic models.
"""

from __future__ import annotations

import logging
from enum import StrEnum

from pydantic import BaseModel

logger = logging.getLogger(__name__)


class JoinType(StrEnum):
    """SQL JOIN types."""

    INNER = "INNER"
    LEFT = "LEFT"
    RIGHT = "RIGHT"
    FULL = "FULL"
    CROSS = "CROSS"


class SortDirection(StrEnum):
    """SQL ORDER BY direction."""

    ASC = "ASC"
    DESC = "DESC"


class RelationalNode(BaseModel):
    """Base class for all Relational IR nodes.

    Attributes:
        alias: Optional alias for the node (used in SQL AS clauses).

    TODO: Add source tracking back to SPL IR nodes for error reporting.
    """

    alias: str | None = None


class ColumnRef(RelationalNode):
    """Reference to a column in a table or subquery.

    Attributes:
        table: Optional table name or alias.
        column: Column name.

    TODO: Add type information for column references.
    """

    table: str | None = None
    column: str


class FilterPredicate(RelationalNode):
    """A WHERE/HAVING filter predicate.

    Attributes:
        expression_text: The raw predicate expression (unparsed for now).

    TODO: Parse into a proper expression tree with operators.
    """

    expression_text: str


class AggregateFunction(RelationalNode):
    """An aggregate function call (COUNT, SUM, AVG, etc.).

    Attributes:
        function_name: The SQL aggregate function name.
        arguments: List of column references or expressions.

    TODO: Add DISTINCT support.
    """

    function_name: str
    arguments: list[str]


class SelectNode(RelationalNode):
    """A SQL SELECT statement node.

    Attributes:
        columns: List of column references or expressions to select.
        from_table: Source table or subquery name.
        where: Optional WHERE clause predicate.
        group_by: Optional GROUP BY column list.
        having: Optional HAVING clause predicate.
        order_by: Optional ORDER BY specifications.
        limit: Optional LIMIT value.

    TODO: Support subqueries in FROM clause.
    TODO: Add DISTINCT support.
    """

    columns: list[str]
    from_table: str
    where: FilterPredicate | None = None
    group_by: list[str] = []
    having: FilterPredicate | None = None
    order_by: list[tuple[str, SortDirection]] = []
    limit: int | None = None


class JoinNode(RelationalNode):
    """A SQL JOIN node.

    Attributes:
        join_type: The type of JOIN (INNER, LEFT, etc.).
        left_table: Left side of the join.
        right_table: Right side of the join.
        on_condition: The JOIN ON condition expression.

    TODO: Support complex join conditions.
    """

    join_type: JoinType
    left_table: str
    right_table: str
    on_condition: str


class RelationalQuery(RelationalNode):
    """Root node representing a complete relational query.

    Attributes:
        select: The top-level SELECT node.

    TODO: Support CTEs (WITH clauses).
    TODO: Support UNION/INTERSECT/EXCEPT.
    """

    select: SelectNode
