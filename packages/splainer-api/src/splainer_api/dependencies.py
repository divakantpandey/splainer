"""FastAPI dependency injection: singletons for config and client."""

from __future__ import annotations

from functools import lru_cache

from spl_to_sql.config import SplToSqlConfig
from splainer_sdk import SplainerClient
from splainer_api.config import APISettings


@lru_cache
def get_api_settings() -> APISettings:
    """Singleton API settings."""
    return APISettings()


@lru_cache
def get_core_config() -> SplToSqlConfig:
    """Singleton core config."""
    return SplToSqlConfig.from_env()


@lru_cache
def get_client() -> SplainerClient:
    """Singleton SplainerClient shared across all requests."""
    config = get_core_config()
    return SplainerClient(config=config)

