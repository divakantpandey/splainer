"""FastAPI application factory and uvicorn entry point."""

from __future__ import annotations

import uvicorn
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from splainer_api._version import __version__
from splainer_api.config import APISettings
from splainer_api.middleware.auth import APIKeyAuth
from splainer_api.middleware.rate_limit import create_limiter
from splainer_api.middleware.logging import RequestLoggingMiddleware
from splainer_api.routes import translate, pipeline, execute, health, dialects


def create_app(settings: APISettings | None = None) -> FastAPI:
    """Application factory for the Splainer REST API."""
    if settings is None:
        settings = APISettings()

    app = FastAPI(
        title="Splainer API",
        description=(
            "REST API for translating Splunk SPL queries into SQL.\n\n"
            "## Features\n"
            "- **Multi-dialect** SQL generation (Postgres, Snowflake, MySQL)\n"
            "- **Hybrid compilation**: deterministic rules + LLM fallback\n"
            "- **Auto-fix loop**: executes SQL and auto-corrects errors via LLM\n"
            "- **Full pipeline introspection**: view intermediate IRs\n"
        ),
        version=__version__,
        docs_url="/docs",           # Swagger UI
        redoc_url="/redoc",         # ReDoc
        openapi_url="/openapi.json",
    )

    # --- CORS ---
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # --- Request Logging ---
    app.add_middleware(RequestLoggingMiddleware)

    # --- Rate Limiting ---
    if settings.rate_limit_enabled:
        limiter = create_limiter()
        app.state.limiter = limiter
        app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

    # --- Auth dependency (applied to all /v1 routes) ---
    auth = APIKeyAuth(settings)

    # --- Routes ---
    app.include_router(health.router)                            # /health — public
    app.include_router(dialects.router, dependencies=[Depends(auth)])    # /v1/dialects
    app.include_router(translate.router, dependencies=[Depends(auth)])   # /v1/translate
    app.include_router(pipeline.router, dependencies=[Depends(auth)])    # /v1/pipeline
    app.include_router(execute.router, dependencies=[Depends(auth)])     # /v1/execute

    return app


def main():
    """CLI entry point: `splainer-api` starts the server."""
    settings = APISettings()
    uvicorn.run(
        "splainer_api.app:create_app",
        host=settings.host,
        port=settings.port,
        workers=settings.workers,
        reload=settings.reload,
        factory=True,
    )

