"""Pydantic models for SPL IR nodes.

These models represent the SPL-shaped intermediate representation.
"""

from __future__ import annotations

import logging
from typing import Any

from pydantic import BaseModel

logger = logging.getLogger(__name__)


class SPLNode(BaseModel):
    source_text: str = ""


# --- Expressions ---
class Expression(SPLNode):
    pass

class FieldRef(Expression):
    field_name: str

class Literal(Expression):
    value: Any

class BinaryOp(Expression):
    left: Expression
    op: str
    right: Expression

class UnaryOp(Expression):
    op: str
    expr: Expression

class FunctionCall(Expression):
    function_name: str
    args: list[Expression] = []

class WildcardExpr(Expression):
    pattern: str

class InExpr(Expression):
    field: Expression
    values: list[Expression]

# --- Commands ---
class EvalAssignment(SPLNode):
    target_field: str
    expression: Expression

class EvalCommand(SPLNode):
    assignments: list[EvalAssignment]

class SearchCommand(SPLNode):
    expression: Expression | None
    index: str | None = None
    sourcetype: str | None = None

class AggregationFunc(SPLNode):
    function_name: str
    field: Expression | None
    alias: str | None = None

class StatsCommand(SPLNode):
    aggregations: list[AggregationFunc]
    group_by: list[Expression] = []

class SortCommand(SPLNode):
    fields: list[str]

class WhereCommand(SPLNode):
    expression: Expression

class TableCommand(SPLNode):
    fields: list[str]

class FieldsCommand(SPLNode):
    fields: list[str]
    keep: bool = True

class HeadCommand(SPLNode):
    count: int

class TailCommand(SPLNode):
    count: int

class RenameItem(SPLNode):
    old_name: str
    new_name: str

class RenameCommand(SPLNode):
    renames: list[RenameItem]

class DedupCommand(SPLNode):
    fields: list[str]

class TopCommand(SPLNode):
    limit: int | None = None
    field: str
    by: list[str] = []

class RareCommand(SPLNode):
    limit: int | None = None
    field: str
    by: list[str] = []

class UnknownCommand(SPLNode):
    command_name: str
    raw_text: str


class PipelineStage(SPLNode):
    command_name: str
    command: (
        SearchCommand
        | StatsCommand
        | SortCommand
        | EvalCommand
        | WhereCommand
        | TableCommand
        | FieldsCommand
        | HeadCommand
        | TailCommand
        | RenameCommand
        | DedupCommand
        | TopCommand
        | RareCommand
        | UnknownCommand
    )


class SPLPipeline(SPLNode):
    stages: list[PipelineStage]

