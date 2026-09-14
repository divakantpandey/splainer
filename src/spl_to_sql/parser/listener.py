"""ANTLR4 parse tree listener/visitor for SPL.

Provides a listener (or visitor) implementation that walks the ANTLR4
parse tree produced by the generated SPL parser. This is the bridge
between raw parse tree nodes and the SPL IR builder.

TODO: Switch to visitor pattern if listener proves awkward for
      building IR nodes (visitors return values, listeners don't).
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from spl_to_sql.ir.spl_ir.nodes import PipelineStage

logger = logging.getLogger(__name__)


class SPLParseTreeListener:
    """Walks an ANTLR4 SPL parse tree and extracts structural information.

    This listener is intended to be subclassed or used directly with
    ANTLR4's ParseTreeWalker. Each enter/exit method corresponds to a
    grammar rule in SPL.g4.

    Attributes:
        errors: List of parse errors encountered during the walk.

    TODO: Implement actual listener methods once ANTLR4 generates code.
    TODO: Decide between listener vs visitor pattern.
    """

    def __init__(self) -> None:
        self.errors: list[str] = []

    def walk(self, tree: Any) -> list[PipelineStage]:
        """Walk the parse tree and return a list of pipeline stages.

        Args:
            tree: The ANTLR4 parse tree root node.

        Returns:
            A list of PipelineStage IR nodes extracted from the tree.

        Raises:
            ParseError: If the tree contains unrecoverable errors.

        TODO: Implement parse tree walking logic.
        """
        # TODO: Implement parse tree walking
        raise NotImplementedError("Parse tree walking not yet implemented")

    def enter_query(self, ctx: Any) -> None:
        """Called when entering a 'query' rule in the parse tree.

        Args:
            ctx: The ANTLR4 parser context for the query rule.

        TODO: Implement query entry logic.
        """
        # TODO: Implement
        raise NotImplementedError

    def exit_query(self, ctx: Any) -> None:
        """Called when exiting a 'query' rule in the parse tree.

        Args:
            ctx: The ANTLR4 parser context for the query rule.

        TODO: Implement query exit logic.
        """
        # TODO: Implement
        raise NotImplementedError

    def enter_command(self, ctx: Any) -> None:
        """Called when entering a 'command' rule in the parse tree.

        Args:
            ctx: The ANTLR4 parser context for the command rule.

        TODO: Implement command entry logic.
        """
        # TODO: Implement
        raise NotImplementedError

    def exit_command(self, ctx: Any) -> None:
        """Called when exiting a 'command' rule in the parse tree.

        Args:
            ctx: The ANTLR4 parser context for the command rule.

        TODO: Implement command exit logic.
        """
        # TODO: Implement
        raise NotImplementedError
