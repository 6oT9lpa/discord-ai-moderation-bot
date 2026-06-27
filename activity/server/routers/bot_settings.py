from typing import Any

from fastapi import APIRouter, Depends, Query

from activity.server.dependencies import require_bearer_token
from activity.server.services.bot_settings_service import BotSettingsService

router = APIRouter()
service = BotSettingsService()


@router.get("/api/bot/settings")
async def get_bot_settings(
    guild_id: int = Query(gt=0),
    access_token: str = Depends(require_bearer_token),
) -> dict[str, Any]:
    return await service.get_settings(guild_id, access_token)
