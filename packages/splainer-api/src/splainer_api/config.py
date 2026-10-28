"""API-specific settings, layered on top of core SplToSqlConfig."""

from __future__ import annotations

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class APISettings(BaseSettings):
    """Settings specific to the Splainer REST API server."""

    # --- Authentication ---
    api_keys: list[str] = Field(
        default_factory=list,
        description="Valid API keys (comma-separated in env var).",
    )
    require_auth: bool = Field(
        default=True,
        description="If False, all endpoints are open (dev mode).",
    )

    # --- Rate Limiting ---
    rate_limit: str = Field(
        default="60/minute",
        description="Default rate limit per API key (slowapi format).",
    )
    rate_limit_enabled: bool = True

    # --- Server ---
    host: str = "0.0.0.0"
    port: int = 8080
    workers: int = 1
    reload: bool = False

    # --- Logging ---
    log_level: str = "INFO"
    log_format: str = "json"  # "json" or "console"

    # --- CORS ---
    cors_origins: list[str] = Field(
        default_factory=lambda: ["*"],
        description="Allowed CORS origins.",
    )

    model_config = SettingsConfigDict(
        env_prefix="SPLAINER_API__",
        env_file="infra/.env",
        env_file_encoding="utf-8",
        extra="ignore",
    )
