"""Abstract SQL dialect interface.

Defines the contract that each dialect-specific module must implement.
Dialects handle differences in SQL syntax across database engines.

TODO: Add more dialect-specific methods as codegen needs grow.
"""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


class SQLDialect(ABC):
    """Abstract base class for SQL dialect-specific rendering.

    Each target database (Postgres, Snowflake, etc.) subclasses this
    to provide its specific SQL syntax.

    TODO: Add more abstract methods as dialect differences are discovered.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """The canonical name of this dialect.

        Returns:
            Dialect name (e.g., 'postgres', 'snowflake').
        """
        ...

    @abstractmethod
    def quote_identifier(self, identifier: str) -> str:
        """Quote a SQL identifier according to this dialect's rules.

        Args:
            identifier: The raw identifier name.

        Returns:
            The quoted identifier string.

        TODO: Implement per dialect.
        """
        ...

    @abstractmethod
    def render_limit(self, limit: int) -> str:
        """Render a row limit clause for this dialect.

        Some dialects use LIMIT, others use TOP, FETCH FIRST, etc.

        Args:
            limit: Maximum number of rows.

        Returns:
            The rendered limit clause string.

        TODO: Implement per dialect.
        """
        ...

    @abstractmethod
    def render_string_literal(self, value: str) -> str:
        """Render a string literal with proper escaping for this dialect.

        Args:
            value: The raw string value.

        Returns:
            The escaped and quoted string literal.

        TODO: Implement per dialect.
        """
        ...
