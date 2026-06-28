from __future__ import annotations

import os
from typing import Any
from urllib.parse import urlparse

import aiohttp

from infrastructure.logging import get_logger


logger = get_logger(__name__)

_PATCHED = False
_ORIGINAL_REQUEST = None
_DISCORD_HOST_SUFFIXES = (
    "discord.com",
    "discordapp.com",
    "discord.gg",
)


def get_discord_proxy_url() -> str | None:
    return (
        os.getenv("DISCORD_PROXY_URL")
        or os.getenv("HTTPS_PROXY")
        or os.getenv("HTTP_PROXY")
        or os.getenv("ALL_PROXY")
    )


def install_aiohttp_discord_proxy() -> None:
    global _PATCHED, _ORIGINAL_REQUEST
    if _PATCHED:
        return

    proxy_url = get_discord_proxy_url()
    if not proxy_url:
        logger.info("Discord aiohttp proxy is not configured")
        return

    _ORIGINAL_REQUEST = aiohttp.ClientSession._request

    async def proxied_request(self: aiohttp.ClientSession, method: str, url: Any, **kwargs: Any):
        if "proxy" not in kwargs and _is_discord_url(str(url)):
            kwargs["proxy"] = proxy_url
        return await _ORIGINAL_REQUEST(self, method, url, **kwargs)

    aiohttp.ClientSession._request = proxied_request
    _PATCHED = True
    logger.info("Discord aiohttp proxy installed proxy=%s", _redact_proxy(proxy_url))


def _is_discord_url(url: str) -> bool:
    host = urlparse(url).hostname
    if not host:
        return False
    return any(host == suffix or host.endswith(f".{suffix}") for suffix in _DISCORD_HOST_SUFFIXES)


def _redact_proxy(proxy_url: str) -> str:
    parsed = urlparse(proxy_url)
    if parsed.username or parsed.password:
        netloc = parsed.hostname or ""
        if parsed.port:
            netloc = f"{netloc}:{parsed.port}"
        return parsed._replace(netloc=netloc).geturl()
    return proxy_url
