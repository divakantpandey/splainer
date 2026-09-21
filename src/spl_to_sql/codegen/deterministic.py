"""Rule-based (deterministic) SQL code generation.

Translates Relational IR nodes into SQL text using pattern-matching
rules. Covers the subset of SQL constructs that can be deterministically
generated without LLM assistance.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from spl_to_sql.codegen.dialects.base import SQLDialect
    from spl_to_sql.ir.relational_ir.nodes import RelationalQuery

logger = logging.getLogger(__name__)


def generate_sql(
    query: RelationalQuery,
    dialect: SQLDialect | None = None,
) -> str:
    select = query.select
    
    parts = []
    # Columns
    cols_str = ", ".join(select.columns) if select.columns else "*"
    parts.append(f"SELECT {cols_str}")
    
    # From
    parts.append(f"FROM {select.from_table}")
    
    # Where
    if select.where:
        parts.append(f"WHERE {select.where.expression_text}")
        
    # Group By
    if select.group_by:
        gb_str = ", ".join(select.group_by)
        parts.append(f"GROUP BY {gb_str}")
        
    # Having
    if select.having:
        parts.append(f"HAVING {select.having.expression_text}")
        
    # Order By
    if select.order_by:
        ob_parts = [f"{col} {dir.value}" for col, dir in select.order_by]
        parts.append(f"ORDER BY {', '.join(ob_parts)}")
        
    # Limit
    if select.limit is not None:
        parts.append(f"LIMIT {select.limit}")
        
    return "\n".join(parts) + ";"
