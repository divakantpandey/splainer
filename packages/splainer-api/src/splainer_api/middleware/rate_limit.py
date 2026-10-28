"""Rate limiting using slowapi, keyed by API key or remote address."""

from __future__ import annotations

from slowapi import Limiter
from slowapi.util import get_remote_address


def create_limiter() -> Limiter:
    """Create a rate limiter that keys on API key (preferred) or IP."""

    def key_func(request):
        api_key = request.headers.get("X-API-Key")
        return api_key if api_key else get_remote_address(request)

    return Limiter(key_func=key_func)

