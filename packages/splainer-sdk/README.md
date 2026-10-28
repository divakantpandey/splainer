# Splainer SDK

Python client for translating Splunk SPL queries into SQL.

## Installation

```bash
uv pip install splainer-sdk
```

## Usage

```python
from splainer_sdk import SplainerClient

client = SplainerClient()
result = client.translate("search index=main | stats count by host")
print(result.sql)
```

Async support:

```python
import asyncio
from splainer_sdk import AsyncSplainerClient

async def main():
    async with AsyncSplainerClient() as client:
        result = await client.translate("search index=main | stats count by host")
        print(result.sql)

asyncio.run(main())
```

