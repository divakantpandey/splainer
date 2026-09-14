"""Parse tree → SPL IR builder.

Converts an ANTLR4 parse tree into the SPL-shaped intermediate
representation. This is the 'convert to AST' step, renamed and
relocated from the original design to clarify that it produces a
specific IR (SPL-shaped), not a generic AST.

TODO: Implement actual parse tree → IR conversion.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from spl_to_sql.ir.spl_ir.nodes import SPLPipeline

logger = logging.getLogger(__name__)


def build_spl_ir(parse_tree: Any) -> SPLPipeline:
    """Build an SPL IR pipeline from an ANTLR4 parse tree.

    This is the main entry point for Stage 2 of the pipeline.
    Takes the raw parse tree produced by the ANTLR4 parser and
    converts it into a structured SPL IR.

    Args:
        parse_tree: The ANTLR4 parse tree root node.

    Returns:
        An SPLPipeline representing the complete query.

    Raises:
        IRLoweringError: If the parse tree contains unsupported
            constructs or is malformed.

    TODO: Implement parse tree traversal and IR node construction.
    """
    # TODO: Implement parse tree → SPL IR conversion
    raise NotImplementedError("SPL IR building not yet implemented")


def _build_search_command(ctx: Any) -> Any:
    """Build a SearchCommand node from a search rule context.

    Args:
        ctx: The ANTLR4 parser context for a searchCommand rule.

    Returns:
        A SearchCommand IR node.

    TODO: Implement search command extraction.
    """
    # TODO: Implement
    raise NotImplementedError


def _build_pipeline_stage(ctx: Any) -> Any:
    """Build a PipelineStage node from a command rule context.

    Args:
        ctx: The ANTLR4 parser context for a command rule.

    Returns:
        A PipelineStage IR node.

    TODO: Implement command dispatch and stage construction.
    """
    # TODO: Implement
    raise NotImplementedError
