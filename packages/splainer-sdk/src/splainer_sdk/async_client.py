"""Asynchronous Splainer client.

Wraps the synchronous client using anyio.to_thread to avoid
blocking the event loop during CPU/IO-bound pipeline operations.
"""

from __future__ import annotations

from functools import partial

import anyio

from splainer_sdk.client import SplainerClient
from splainer_sdk.models import (
    Dialect,
    TranslateResult,
    PipelineDetail,
    HealthStatus,
)


class AsyncSplainerClient:
    """Async wrapper around SplainerClient.

    Usage::

        async with AsyncSplainerClient() as client:
            result = await client.translate("search index=main | stats count by host")
            print(result.sql)
    """

    def __init__(self, **kwargs):
        """Accepts same arguments as SplainerClient."""
        self._sync_client = SplainerClient(**kwargs)

    async def translate(
        self,
        spl_query: str,
        *,
        dialect: Dialect | str | None = None,
        execute: bool = False,
    ) -> TranslateResult:
        """Async translate an SPL query to SQL."""
        return await anyio.to_thread.run_sync(
            partial(
                self._sync_client.translate,
                spl_query,
                dialect=dialect,
                execute=execute,
            )
        )

    async def translate_simple(
        self,
        spl_query: str,
        dialect: Dialect | str | None = None,
    ) -> str:
        """Async convenience: translate and return just the SQL string."""
        return await anyio.to_thread.run_sync(
            partial(self._sync_client.translate_simple, spl_query, dialect=dialect)
        )

    async def get_pipeline_detail(
        self,
        spl_query: str,
        dialect: Dialect | str | None = None,
    ) -> PipelineDetail:
        """Async run the full pipeline with intermediate representations."""
        return await anyio.to_thread.run_sync(
            partial(
                self._sync_client.get_pipeline_detail,
                spl_query,
                dialect=dialect,
            )
        )

    async def health(self) -> HealthStatus:
        """Async health check (lightweight, no thread needed)."""
        return self._sync_client.health()

    @property
    def supported_dialects(self) -> list[str]:
        return self._sync_client.supported_dialects

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        pass

