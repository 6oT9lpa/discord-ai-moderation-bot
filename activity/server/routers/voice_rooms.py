from typing import Any

from fastapi import APIRouter, Depends, Query

from activity.server.dependencies import require_bearer_token
from activity.server.schemas.voice_rooms import VoiceRoomUpdatePayload
from activity.server.services.voice_room_service import VoiceRoomService

router = APIRouter()
service = VoiceRoomService()


@router.get("/api/voice/rooms")
async def list_voice_rooms(
    guild_id: int = Query(gt=0),
    access_token: str = Depends(require_bearer_token),
) -> list[dict[str, Any]]:
    return await service.list_rooms(guild_id, access_token)


@router.patch("/api/voice/rooms/{channel_id}")
async def update_voice_room(
    channel_id: int,
    payload: VoiceRoomUpdatePayload,
    access_token: str = Depends(require_bearer_token),
) -> dict[str, Any]:
    return await service.update_room(channel_id, payload, access_token)


@router.delete("/api/voice/rooms/{channel_id}")
async def delete_voice_room(
    channel_id: int,
    guild_id: int = Query(gt=0),
    access_token: str = Depends(require_bearer_token),
) -> dict[str, Any]:
    return await service.delete_room(channel_id, guild_id, access_token)
