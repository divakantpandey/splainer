from __future__ import annotations

from enum import Enum
from pydantic import BaseModel, Field


class Dialect(str, Enum):
    """Supported SQL dialects."""
    POSTGRES = "postgres"
    SNOWFLAKE = "snowflake"
    MYSQL = "mysql"


class TranslateRequest(BaseModel):
    """Request to translate an SPL query to SQL."""
    spl_query: str = Field(..., description="The SPL query string to translate.")
    dialect: Dialect = Field(default=Dialect.POSTGRES, description="Target SQL dialect.")
    execute: bool = Field(default=False, description="Whether to execute the generated SQL.")


class PipelineStep(BaseModel):
    """Information about a single step in the translation pipeline."""
    name: str
    status: str
    message: str
    duration_ms: float | None = None


class ExecutionDetail(BaseModel):
    """Result of executing SQL against a database."""
    success: bool
    rows: list[dict] | None = None
    error: str | None = None
    row_count: int = 0


class TranslateResult(BaseModel):
    """Result of an SPL-to-SQL translation."""
    spl_query: str
    sql: str
    dialect: str
    success: bool
    used_llm: bool = False
    codegen_route: str = "deterministic"
    error: str | None = None
    execution_result: list[dict] | None = None
    pipeline_steps: list[PipelineStep] = Field(default_factory=list)


class PipelineDetail(BaseModel):
    """Full pipeline output including intermediate representations."""
    spl_query: str
    sql: str | None = None
    dialect: str
    spl_ir_summary: str | None = None
    relational_ir_summary: str | None = None
    used_llm: bool = False
    codegen_route: str = "deterministic"
    steps: list[PipelineStep] = Field(default_factory=list)
    error: str | None = None


class HealthStatus(BaseModel):
    """API health check response."""
    status: str  # "healthy" | "degraded"
    version: str
    llm_configured: bool
    db_configured: bool

