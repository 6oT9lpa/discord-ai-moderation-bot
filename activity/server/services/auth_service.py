import os
from typing import Any

import httpx
from fastapi import HTTPException

from activity.server.config import activity_server_config
from activity.server.schemas.auth import TokenRequest


class ActivityAuthService:
    async def exchange_token(self, payload: TokenRequest) -> dict[str, Any]:
        client_id = os.getenv("DISCORD_CLIENT_ID")
        client_secret = os.getenv("DISCORD_CLIENT_SECRET")

        if not client_id or not client_secret:
            raise HTTPException(
                status_code=500,
                detail="DISCORD_CLIENT_ID and DISCORD_CLIENT_SECRET are required",
            )

        data = {
            "client_id": client_id,
            "client_secret": client_secret,
            "grant_type": "authorization_code",
            "code": payload.code,
        }

        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.post(
                f"{activity_server_config.discord_api_base}/oauth2/token",
                data=data,
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )

        if response.status_code >= 400:
            raise HTTPException(status_code=response.status_code, detail=response.text)

        token = response.json()
        return {
            "access_token": token["access_token"],
            "token_type": token.get("token_type", "Bearer"),
            "expires_in": token.get("expires_in", 0),
            "scope": token.get("scope", ""),
        }
