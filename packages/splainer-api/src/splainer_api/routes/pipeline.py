"""POST /v1/pipeline — Full pipeline with intermediate IR results."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from splainer_sdk import SplainerClient, Dialect, PipelineDetail
from splainer_api.dependencies import get_client

router = APIRouter(prefix="/v1", tags=["Pipeline"])


class PipelineRequest(BaseModel):
    spl_query: str = Field(
        ..., description="SPL query to process through the full pipeline."
    )
    dialect: Dialect = Field(default=Dialect.POSTGRES)


@router.post(
    "/pipeline",
    response_model=PipelineDetail,
    summary="Full pipeline with intermediate results",
    description=(
        "Runs the SPL query through every pipeline stage and returns "
        "intermediate representations (SPL IR, Relational IR) alongside "
        "the final SQL. Does NOT execute the query."
    ),
)
async def pipeline_detail(
    request: PipelineRequest,
    client: SplainerClient = Depends(get_client),
) -> PipelineDetail:
    try:
        return client.get_pipeline_detail(
            request.spl_query, dialect=request.dialect
        )
    except Exception as exc:
        raise HTTPException(status_code=422, detail=str(exc))

