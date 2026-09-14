"""Pydantic models for SPL IR nodes.

These models represent the SPL-shaped intermediate representation.
Each node type corresponds to a concept in SPL's semantics.

TODO: Add more node types as SPL commands are supported.
TODO: Add validation rules to pydantic models.
"""

from __future__ import annotations

import logging

from pydantic import BaseModel

logger = logging.getLogger(__name__)


class SPLNode(BaseModel):
    """Base class for all SPL IR nodes.

    Attributes:
        source_text: Original SPL text fragment this node was derived from.

    TODO: Add source location tracking (line/col) for error messages.
    """

    source_text: str = ""


class FieldReference(SPLNode):
    """Reference to a field (column) in the SPL data model.

    Attributes:
        field_name: The name of the field being referenced.

    TODO: Add field type inference support.
    """

    field_name: str


class EvalExpression(SPLNode):
    """An eval expression in SPL (e.g., ``eval new_field=old_field * 2``).

    Attributes:
        target_field: The field being assigned to.
        expression_text: The raw expression text (unparsed for now).

    TODO: Parse expression_text into a proper expression tree.
    """

    target_field: str
    expression_text: str


class SearchCommand(SPLNode):
    """The implicit or explicit 'search' command.

    Attributes:
        search_expression: The search filter expression text.
        index: Optional index name constraint.
        sourcetype: Optional sourcetype constraint.

    TODO: Parse search_expression into structured filter predicates.
    """

    search_expression: str
    index: str | None = None
    sourcetype: str | None = None


class StatsCommand(SPLNode):
    """The 'stats' command for aggregation.

    Attributes:
        aggregations: List of aggregation function calls (e.g., 'count', 'avg(field)').
        group_by_fields: Fields to group by.

    TODO: Parse aggregation functions into structured representations.
    """

    aggregations: list[str]
    group_by_fields: list[str] = []


class SortCommand(SPLNode):
    """The 'sort' command for ordering results.

    Attributes:
        fields: Fields to sort by, with optional '-' prefix for descending.

    TODO: Parse sort direction into a structured enum.
    """

    fields: list[str]


class PipelineStage(SPLNode):
    """A single stage (command) in the SPL pipeline.

    Attributes:
        command: The command node (SearchCommand, StatsCommand, etc.).
        command_name: The name of the SPL command.

    TODO: Use a proper union type for command once all command types exist.
    """

    command_name: str
    command: SearchCommand | StatsCommand | SortCommand | EvalExpression


class SPLPipeline(SPLNode):
    """Root node representing a complete SPL pipeline (query).

    Attributes:
        stages: Ordered list of pipeline stages.

    TODO: Add pipeline-level validation.
    """

    stages: list[PipelineStage]
