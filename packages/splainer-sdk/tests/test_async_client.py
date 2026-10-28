import pytest
from splainer_sdk import AsyncSplainerClient

@pytest.mark.asyncio
async def test_async_health():
    async with AsyncSplainerClient() as client:
        health = await client.health()
        assert health.status == "healthy"

