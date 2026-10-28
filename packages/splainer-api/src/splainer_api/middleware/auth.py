"""API Key authentication via X-API-Key header."""

from __future__ import annotations

from fastapi import Request, HTTPException, Security
from fastapi.security import APIKeyHeader

from splainer_api.config import APISettings

API_KEY_HEADER = APIKeyHeader(name="X-API-Key", auto_error=False)


class APIKeyAuth:
    """Dependency that validates API key from request header."""

    def __init__(self, settings: APISettings):
        self.settings = settings

    async def __call__(
        self,
        request: Request,
        api_key: str | None = Security(API_KEY_HEADER),
    ) -> str | None:
        if not self.settings.require_auth:
            return None

        if not api_key:
            raise HTTPException(
                status_code=401,
                detail="Missing API key. Provide it via the X-API-Key header.",
            )

        if api_key not in self.settings.api_keys:
            raise HTTPException(
                status_code=403,
                detail="Invalid API key.",
            )

        return api_key

