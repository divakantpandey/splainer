"""SPL IR → Relational IR lowering.

Transforms the SPL-shaped IR into a relational-algebra-shaped IR.
"""

from __future__ import annotations

import logging
from typing import Any

from spl_to_sql.ir.relational_ir.nodes import (
    RelationalQuery,
    SelectNode,
    FilterPredicate,
)
from spl_to_sql.ir.spl_ir.nodes import (
    SPLPipeline,
    SearchCommand,
    StatsCommand,
    EvalCommand,
    WhereCommand,
    TableCommand,
    FieldsCommand,
    SortCommand,
    HeadCommand,
    TailCommand,
    RenameCommand,
    DedupCommand,
    TopCommand,
    RareCommand,
    Expression,
    BinaryOp,
    UnaryOp,
    FieldRef,
    Literal,
    WildcardExpr,
    InExpr,
    FunctionCall
)

logger = logging.getLogger(__name__)

def _lower_expression(expr: Expression) -> str:
    if isinstance(expr, BinaryOp):
        left = _lower_expression(expr.left)
        right = _lower_expression(expr.right)
        op = expr.op.upper()
        return f"({left} {op} {right})"
    elif isinstance(expr, UnaryOp):
        return f"{expr.op.upper()} ({_lower_expression(expr.expr)})"
    elif isinstance(expr, FieldRef):
        return expr.field_name
    elif isinstance(expr, Literal):
        if isinstance(expr.value, str):
            # very naive escaping for MVP
            val = expr.value.replace("'", "''")
            return f"'{val}'"
        elif expr.value is None:
            return "NULL"
        return str(expr.value)
    elif isinstance(expr, WildcardExpr):
        return "'%'"
    elif isinstance(expr, InExpr):
        field = _lower_expression(expr.field)
        values = ", ".join([_lower_expression(v) for v in expr.values])
        return f"{field} IN ({values})"
    else:
        raise ValueError(f"Unknown expression type: {type(expr)}")

def lower_to_relational(spl_pipeline: SPLPipeline) -> RelationalQuery:
    if not spl_pipeline.stages:
        raise ValueError("Empty pipeline")
        
    first_stage = spl_pipeline.stages[0].command
    if not isinstance(first_stage, SearchCommand):
        raise ValueError("First stage must be search")
        
    table_name = "events"
    
    # Helper to find index in expression tree
    def extract_index(expr: Expression | None) -> str | None:
        if not expr:
            return None
        if isinstance(expr, BinaryOp):
            if expr.op == "=" and isinstance(expr.left, FieldRef) and expr.left.field_name == "index":
                return str(expr.right.value) if isinstance(expr.right, Literal) else None
            elif expr.op == "AND":
                left_idx = extract_index(expr.left)
                if left_idx: return left_idx
                return extract_index(expr.right)
        return None
        
    # Helper to remove the index filter from the expression tree
    def remove_index_expr(expr: Expression | None) -> Expression | None:
        if not expr:
            return None
        if isinstance(expr, BinaryOp):
            if expr.op == "=" and isinstance(expr.left, FieldRef) and expr.left.field_name == "index":
                return None
            elif expr.op == "AND":
                left_clean = remove_index_expr(expr.left)
                right_clean = remove_index_expr(expr.right)
                if left_clean and right_clean:
                    return BinaryOp(left=left_clean, op="AND", right=right_clean)
                return left_clean or right_clean
        return expr

    extracted = extract_index(first_stage.expression)
    if extracted:
        table_name = extracted
        
    cleaned_expr = remove_index_expr(first_stage.expression)

    where = None
    if cleaned_expr:
        expr_str = _lower_expression(cleaned_expr)
        where = FilterPredicate(expression_text=expr_str)
            
    select_node = SelectNode(
        columns=["*"],
        from_table=table_name,
        where=where,
    )
    
    for stage in spl_pipeline.stages[1:]:
        cmd = stage.command
        
        if isinstance(cmd, StatsCommand):
            select_node.columns = []
            for agg in cmd.aggregations:
                func = agg.function_name.upper() if agg.function_name else "COUNT"
                if func == "COUNT" and not agg.field:
                    col = "COUNT(*) AS count"
                else:
                    field = _lower_expression(agg.field) if agg.field else "*"
                    col = f"{func}({field})"
                    if agg.alias:
                        col += f" AS {agg.alias}"
                select_node.columns.append(col)
                    
            if cmd.group_by:
                for gb in cmd.group_by:
                    col = _lower_expression(gb)
                    select_node.columns.append(col)
                    select_node.group_by.append(col)
                    
        elif isinstance(cmd, EvalCommand):
            for assign in cmd.assignments:
                expr_str = _lower_expression(assign.expression)
                col = f"{expr_str} AS {assign.target_field}"
                if "*" in select_node.columns:
                    # Append it if * is present
                    select_node.columns.append(col)
                else:
                    # In a real compiler, we'd add to the subquery. MVP: just append
                    select_node.columns.append(col)
                    
        elif isinstance(cmd, WhereCommand):
            expr_str = _lower_expression(cmd.expression)
            if select_node.where:
                select_node.where.expression_text = f"({select_node.where.expression_text}) AND ({expr_str})"
            else:
                select_node.where = FilterPredicate(expression_text=expr_str)
                
        elif isinstance(cmd, TableCommand):
            select_node.columns = cmd.fields.copy()
            
        elif isinstance(cmd, FieldsCommand):
            if cmd.keep:
                select_node.columns = cmd.fields.copy()
            else:
                # MVP: Removing fields requires schema knowledge, just skip for MVP
                pass
                
        elif isinstance(cmd, SortCommand):
            from spl_to_sql.ir.relational_ir.nodes import SortDirection
            select_node.order_by = []
            for field in cmd.fields:
                if field.startswith("-"):
                    select_node.order_by.append((field[1:], SortDirection.DESC))
                elif field.startswith("+"):
                    select_node.order_by.append((field[1:], SortDirection.ASC))
                else:
                    select_node.order_by.append((field, SortDirection.ASC))
                    
        elif isinstance(cmd, HeadCommand):
            select_node.limit = cmd.count
            
        elif isinstance(cmd, TailCommand):
            # Tail requires sorting backward or subqueries. MVP: limit
            select_node.limit = cmd.count
            
        elif isinstance(cmd, RenameCommand):
            for rename in cmd.renames:
                # Need to update column list. MVP: just add an alias
                new_col = f"{rename.old_name} AS {rename.new_name}"
                if "*" in select_node.columns:
                    select_node.columns.append(new_col)
                else:
                    # Replace existing
                    new_cols = []
                    for c in select_node.columns:
                        if c == rename.old_name or c.endswith(f" AS {rename.old_name}"):
                            # Too complex for regex, just replace simple names
                            new_cols.append(new_col)
                        else:
                            new_cols.append(c)
                    select_node.columns = new_cols
                    
        elif isinstance(cmd, DedupCommand):
            # Dedup maps to DISTINCT or ROW_NUMBER(). MVP: DISTINCT on columns
            # But we can't easily model ROW_NUMBER without CTE.
            pass
            
        elif isinstance(cmd, TopCommand):
            select_node.columns = [cmd.field, "COUNT(*) AS count"]
            select_node.group_by = [cmd.field] + cmd.by
            from spl_to_sql.ir.relational_ir.nodes import SortDirection
            select_node.order_by = [("count", SortDirection.DESC)]
            if cmd.limit is not None:
                select_node.limit = cmd.limit
            else:
                select_node.limit = 10
                
        elif isinstance(cmd, RareCommand):
            select_node.columns = [cmd.field, "COUNT(*) AS count"]
            select_node.group_by = [cmd.field] + cmd.by
            from spl_to_sql.ir.relational_ir.nodes import SortDirection
            select_node.order_by = [("count", SortDirection.ASC)]
            if cmd.limit is not None:
                select_node.limit = cmd.limit
            else:
                select_node.limit = 10
        else:
            from spl_to_sql.exceptions import CodegenError
            raise CodegenError(f"Unsupported SPL command type for deterministic lowering: {type(cmd).__name__}")
                
    return RelationalQuery(select=select_node)
