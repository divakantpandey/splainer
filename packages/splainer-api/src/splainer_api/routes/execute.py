"""POST /v1/execute — Translate + execute + auto-fix feedback loop."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from splainer_sdk import SplainerClient, Dialect
from splainer_sdk.exceptions import TranslationError, ExecutionError
from splainer_api.dependencies import get_client

router = APIRouter(prefix="/v1", tags=["Execution"])


class ExecuteRequest(BaseModel):
    spl_query: str = Field(
        ..., description="SPL query to translate and execute."
    )
    dialect: Dialect = Field(default=Dialect.POSTGRES)


class ExecuteResponse(BaseModel):
    spl_query: str
    sql: str
    dialect: str
    success: bool
    used_llm: bool = False
    rows: list[dict] | None = None
    row_count: int = 0
    error: str | None = None
    pipeline_steps: list[dict] = Field(default_factory=list)


@router.post(
    "/execute",
    response_model=ExecuteResponse,
    summary="Translate SPL and execute SQL",
    description=(
        "Translates an SPL query, executes the resulting SQL against the "
        "configured database, and returns the results. Includes the "
        "LLM auto-fix feedback loop if execution fails."
    ),
    responses={
        422: {"description": "Translation or execution failed"},
    },
)
async def execute(
    request: ExecuteRequest,
    client: SplainerClient = Depends(get_client),
) -> ExecuteResponse:
    try:
        result = client.translate(
            request.spl_query,
            dialect=request.dialect,
            execute=True,
        )
    except (TranslationError, ExecutionError) as exc:
        raise HTTPException(status_code=422, detail=str(exc))

    exec_rows = result.execution_result
    return ExecuteResponse(
        spl_query=result.spl_query,
        sql=result.sql,
        dialect=result.dialect,
        success=result.success,
        used_llm=result.used_llm,
        rows=exec_rows,
        row_count=len(exec_rows) if exec_rows else 0,
        error=result.error,
        pipeline_steps=[step.model_dump() for step in result.pipeline_steps],
    )

