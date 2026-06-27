from typing import Any

from fastapi import APIRouter

from activity.server.schemas.auth import TokenRequest, TokenResponse
from activity.server.services.auth_service import ActivityAuthService

router = APIRouter()
service = ActivityAuthService()


@router.post("/api/auth/token", response_model=TokenResponse)
async def exchange_token(payload: TokenRequest) -> dict[str, Any]:
    return await service.exchange_token(payload)
