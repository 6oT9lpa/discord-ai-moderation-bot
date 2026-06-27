from fastapi import APIRouter, Depends, Query

from activity.server.dependencies import require_bearer_token
from activity.server.schemas.activity import ChannelPurposePayload
from activity.server.services.channel_purpose_service import ChannelPurposeService

router = APIRouter()
service = ChannelPurposeService()


@router.get("/api/activity/channel-purposes")
async def get_channel_purposes(
    guild_id: int = Query(gt=0),
    access_token: str = Depends(require_bearer_token),
) -> dict[str, int]:
    return await service.get_channel_purposes(guild_id, access_token)


@router.put("/api/activity/channel-purposes")
async def save_channel_purpose(
    payload: ChannelPurposePayload,
    access_token: str = Depends(require_bearer_token),
) -> dict[str, int]:
    return await service.save_channel_purpose(payload, access_token)
