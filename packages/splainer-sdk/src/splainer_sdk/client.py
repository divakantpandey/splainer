"""Synchronous Splainer client."""

from __future__ import annotations

from spl_to_sql.config import SplToSqlConfig, SqlDialect, LLMProviderConfig
from spl_to_sql.agent import run_pipeline
from spl_to_sql.parser import parse
from spl_to_sql.exceptions import SplToSqlError

from splainer_sdk.models import (
    Dialect,
    TranslateResult,
    PipelineStep,
    PipelineDetail,
    HealthStatus,
)
from splainer_sdk.exceptions import TranslationError, ParseError
from splainer_sdk._version import __version__


class SplainerClient:
    """Synchronous client for SPL-to-SQL translation.

    Usage::

        client = SplainerClient()
        result = client.translate("search index=main | stats count by host")
        print(result.sql)

    Or with custom configuration::

        client = SplainerClient(
            dialect=Dialect.MYSQL,
            db_connection_string="mysql+pymysql://user:pass@localhost/db",
            llm_api_key="sk-...",
        )
    """

    def __init__(
        self,
        *,
        dialect: Dialect | str = Dialect.POSTGRES,
        db_connection_string: str | None = None,
        llm_api_key: str | None = None,
        llm_model: str | None = None,
        llm_base_url: str | None = None,
        config: SplToSqlConfig | None = None,
    ):
        """Initialize the client.

        Args:
            dialect: Default SQL dialect for translations.
            db_connection_string: Database connection string for execution.
            llm_api_key: API key for LLM provider.
            llm_model: LLM model name.
            llm_base_url: Base URL for LLM provider (for local models).
            config: Override with a pre-configured SplToSqlConfig object.
        """
        if config is not None:
            self._config = config
        else:
            self._config = SplToSqlConfig.from_env()

        # Apply overrides
        if db_connection_string:
            self._config.database.connection_string = db_connection_string
        if llm_api_key:
            if self._config.llm is None:
                self._config.llm = LLMProviderConfig()
            self._config.llm.api_key = llm_api_key
        if llm_model and self._config.llm:
            self._config.llm.model_name = llm_model
        if llm_base_url and self._config.llm:
            self._config.llm.base_url = llm_base_url

        self._default_dialect = (
            dialect.value if isinstance(dialect, Dialect) else dialect
        )

    def translate(
        self,
        spl_query: str,
        *,
        dialect: Dialect | str | None = None,
        execute: bool = False,
    ) -> TranslateResult:
        """Translate an SPL query to SQL.

        This runs the full agent pipeline, including LLM fallback
        for unsupported commands and the auto-fix feedback loop
        when execute=True.

        Args:
            spl_query: The SPL query to translate.
            dialect: Target SQL dialect (overrides default).
            execute: Whether to run the SQL against the database.

        Returns:
            TranslateResult with generated SQL and metadata.

        Raises:
            TranslationError: If translation fails irrecoverably.
        """
        target_dialect = self._resolve_dialect(dialect)

        try:
            result = run_pipeline(
                query=spl_query,
                dialect=target_dialect,
                execute=execute,
                config_override=self._config,
            )
        except SplToSqlError as exc:
            raise TranslationError(f"Translation failed: {exc}") from exc
        except Exception as exc:
            raise TranslationError(f"Unexpected error: {exc}") from exc

        steps = _extract_steps(result.agent_logs)

        return TranslateResult(
            spl_query=spl_query,
            sql=result.sql,
            dialect=target_dialect,
            success=result.error is None and bool(result.sql),
            used_llm=result.used_llm,
            codegen_route=result.codegen_route,
            error=result.error,
            execution_result=result.execution_result or None,
            pipeline_steps=steps,
        )

    def translate_simple(
        self,
        spl_query: str,
        dialect: Dialect | str | None = None,
    ) -> str:
        """Convenience: translate and return just the SQL string.

        Raises:
            TranslationError: If translation fails.
        """
        result = self.translate(spl_query, dialect=dialect)
        if not result.success:
            raise TranslationError(result.error or "Translation failed")
        return result.sql

    def parse_spl(self, spl_query: str) -> dict:
        """Parse an SPL query and return parse tree info.

        Useful for debugging and validation.

        Returns:
            dict with 'success' and 'tree_text' keys.
        """
        try:
            tree = parse(spl_query)
            return {"success": True, "tree_text": tree.toStringTree()}
        except SplToSqlError as exc:
            raise ParseError(f"Parse failed: {exc}") from exc

    def get_pipeline_detail(
        self,
        spl_query: str,
        dialect: Dialect | str | None = None,
    ) -> PipelineDetail:
        """Run the full pipeline and return intermediate representations.

        This is useful for debugging and understanding the translation
        steps. Does NOT execute the query.
        """
        target_dialect = self._resolve_dialect(dialect)

        try:
            result = run_pipeline(
                query=spl_query,
                dialect=target_dialect,
                execute=False,
                config_override=self._config,
            )
        except SplToSqlError as exc:
            raise TranslationError(f"Pipeline failed: {exc}") from exc

        steps = _extract_steps(result.agent_logs)

        # Extract IR summaries from agent logs
        spl_ir_summary = None
        rel_ir_summary = None
        for log in result.agent_logs:
            if log.get("node") == "ir_build" and log.get("status") == "success":
                spl_ir_summary = log.get("message", "")
            if log.get("node") == "lowering" and log.get("status") == "success":
                rel_ir_summary = log.get("message", "")

        return PipelineDetail(
            spl_query=spl_query,
            sql=result.sql or None,
            dialect=target_dialect,
            spl_ir_summary=spl_ir_summary,
            relational_ir_summary=rel_ir_summary,
            used_llm=result.used_llm,
            codegen_route=result.codegen_route,
            steps=steps,
            error=result.error,
        )

    def health(self) -> HealthStatus:
        """Check the health of the translation engine."""
        return HealthStatus(
            status="healthy",
            version=__version__,
            llm_configured=self._config.llm is not None and bool(
                self._config.llm.api_key.get_secret_value()
            ),
            db_configured=bool(
                self._config.database.connection_string.get_secret_value()
            ),
        )

    @property
    def supported_dialects(self) -> list[str]:
        """Return list of supported SQL dialects."""
        return [d.value for d in SqlDialect]

    def _resolve_dialect(self, dialect: Dialect | str | None) -> str:
        if dialect is None:
            return self._default_dialect
        return dialect.value if isinstance(dialect, Dialect) else dialect


def _extract_steps(agent_logs: list[dict]) -> list[PipelineStep]:
    """Convert agent_logs from PipelineResult to PipelineStep list."""
    steps = []
    for log in agent_logs:
        steps.append(
            PipelineStep(
                name=log.get("node", "unknown"),
                status=log.get("status", "unknown"),
                message=log.get("message", ""),
                duration_ms=log.get("duration_ms"),
            )
        )
    return steps

