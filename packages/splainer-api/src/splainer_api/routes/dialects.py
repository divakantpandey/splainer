"""GET /v1/dialects — List supported SQL dialects."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from splainer_sdk import SplainerClient
from splainer_api.dependencies import get_client

router = APIRouter(prefix="/v1", tags=["Dialects"])


class DialectsResponse(BaseModel):
    dialects: list[str]


@router.get(
    "/dialects",
    response_model=DialectsResponse,
    summary="List supported SQL dialects",
)
async def list_dialects(
    client: SplainerClient = Depends(get_client),
) -> DialectsResponse:
    return DialectsResponse(dialects=client.supported_dialects)

