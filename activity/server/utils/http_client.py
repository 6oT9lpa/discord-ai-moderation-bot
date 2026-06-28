from __future__ import annotations

import httpx

from infrastructure.config import get_config


def discord_async_client(timeout: float | httpx.Timeout = 10) -> httpx.AsyncClient:
    return httpx.AsyncClient(
        timeout=timeout,
        proxy=get_config().discord_proxy_url,
        trust_env=True,
    )
