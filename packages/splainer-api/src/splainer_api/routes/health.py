"""GET /health — Public health check (no auth required)."""

from __future__ import annotations

from fastapi import APIRouter, Depends

from splainer_sdk import SplainerClient, HealthStatus
from splainer_api.dependencies import get_client

router = APIRouter(tags=["Health"])


@router.get(
    "/health",
    response_model=HealthStatus,
    summary="Health check",
    description="Returns the health status of the API and its dependencies.",
)
async def health(
    client: SplainerClient = Depends(get_client),
) -> HealthStatus:
    return client.health()

