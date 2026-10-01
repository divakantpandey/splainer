"""SQL execution runner.

Executes generated SQL against a target database and returns
results or structured error information.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

from spl_to_sql.exceptions import ExecutionError

if TYPE_CHECKING:
    from sqlalchemy.engine import Engine
    from spl_to_sql.config import DatabaseConfig

logger = logging.getLogger(__name__)


class SQLRunner:
    """Executes SQL queries against a target database.

    Uses SQLAlchemy for database connectivity. The engine is created
    lazily on first use.

    Attributes:
        config: Database connection configuration.
    """

    def __init__(self, config: DatabaseConfig) -> None:
        self.config = config
        self._engine: Engine | None = None

    @property
    def engine(self) -> Engine:
        if self._engine is None:
            conn_str = self.config.connection_string.get_secret_value()
            if not conn_str:
                raise ExecutionError(
                    "Database connection string not configured. "
                    "Set DB_CONNECTION_STRING.",
                    sql="",
                    db_error="Missing connection string",
                )
            logger.info("Creating database engine")
            self._engine = create_engine(
                conn_str,
                pool_pre_ping=True,
                connect_args={"connect_timeout": self.config.timeout_seconds},
            )
        return self._engine

    def execute(self, sql: str) -> list[dict[str, Any]]:
        logger.info("Executing SQL: %s", sql[:200])
        try:
            with self.engine.connect() as conn:
                result = conn.execute(
                    text(sql),
                    execution_options={"timeout": self.config.timeout_seconds},
                )
                rows = [dict(row._mapping) for row in result]
                logger.info("Query returned %d rows", len(rows))
                return rows
        except SQLAlchemyError as e:
            logger.error("SQL execution failed: %s", e)
            raise ExecutionError(
                message=f"SQL execution failed: {e}",
                sql=sql,
                db_error=str(e),
            ) from e

    def validate_connection(self) -> bool:
        try:
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            logger.info("Database connection validated")
            return True
        except Exception as e:
            logger.warning("Database connection validation failed: %s", e)
            return False
