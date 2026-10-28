"""POST /v1/translate — SPL-to-SQL translation endpoint."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from splainer_sdk import SplainerClient, Dialect
from splainer_sdk.exceptions import TranslationError
from splainer_api.dependencies import get_client

router = APIRouter(prefix="/v1", tags=["Translation"])


class TranslateRequest(BaseModel):
    """Request body for SPL-to-SQL translation."""

    spl_query: str = Field(
        ...,
        description="The SPL query string to translate.",
        examples=["search index=main | stats count by host"],
    )
    dialect: Dialect = Field(
        default=Dialect.POSTGRES,
        description="Target SQL dialect.",
    )


class TranslateResponse(BaseModel):
    """Response body for SPL-to-SQL translation."""

    spl_query: str
    sql: str
    dialect: str
    success: bool
    used_llm: bool = False
    codegen_route: str = "deterministic"
    error: str | None = None
    pipeline_steps: list[dict] = Field(default_factory=list)


@router.post(
    "/translate",
    response_model=TranslateResponse,
    summary="Translate SPL to SQL",
    description=(
        "Translates a Splunk SPL query into the target SQL dialect. "
        "Uses deterministic compilation when possible, with LLM fallback "
        "for unsupported commands."
    ),
    responses={
        422: {"description": "Translation failed (parse error, codegen error, etc.)"},
    },
)
async def translate(
    request: TranslateRequest,
    client: SplainerClient = Depends(get_client),
) -> TranslateResponse:
    try:
        result = client.translate(request.spl_query, dialect=request.dialect)
    except TranslationError as exc:
        raise HTTPException(status_code=422, detail=str(exc))

    return TranslateResponse(
        spl_query=result.spl_query,
        sql=result.sql,
        dialect=result.dialect,
        success=result.success,
        used_llm=result.used_llm,
        codegen_route=result.codegen_route,
        error=result.error,
        pipeline_steps=[step.model_dump() for step in result.pipeline_steps],
    )

