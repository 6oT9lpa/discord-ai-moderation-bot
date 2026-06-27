from typing import Any

from activity.server.dependencies import get_db
from activity.server.schemas.voice_rooms import VoiceRoomUpdatePayload
from activity.server.services.access_service import ActivityAccessService
from activity.server.services.discord_service import DiscordService
from activity.server.utils.voice_permissions import build_voice_lock_overwrites


class VoiceRoomService:
    def __init__(self) -> None:
        self._access_service = ActivityAccessService()
        self._discord = DiscordService()

    async def list_rooms(self, guild_id: int, access_token: str) -> list[dict[str, Any]]:
        await self._access_service.ensure_panel_access(access_token, str(guild_id))
        rooms = await get_db().fetch_all(
            "SELECT * FROM voice_rooms WHERE guild_id = ? ORDER BY created_at DESC",
            (guild_id,),
        )
        results = []
        for room in rooms:
            channel = await self._discord.safe_bot_request("GET", f"/channels/{room['channel_id']}")
            results.append({**room, "discord": channel})
        return results

    async def update_room(self, channel_id: int, payload: VoiceRoomUpdatePayload, access_token: str) -> dict[str, Any]:
        await self._access_service.ensure_panel_access(access_token, str(payload.guild_id))
        patch: dict[str, Any] = {}
        if payload.name is not None:
            patch["name"] = payload.name
        if payload.user_limit is not None:
            patch["user_limit"] = payload.user_limit
        if payload.locked is not None:
            channel = await self._discord.bot_request("GET", f"/channels/{channel_id}")
            patch["permission_overwrites"] = build_voice_lock_overwrites(channel, payload.guild_id, payload.locked)
        if patch:
            await self._discord.bot_request("PATCH", f"/channels/{channel_id}", json_body=patch)
        if payload.owner_id is not None:
            await get_db().execute("UPDATE voice_rooms SET owner_id = ? WHERE channel_id = ?", (payload.owner_id, channel_id))
        if payload.persistent is not None:
            await get_db().execute(
                "UPDATE voice_rooms SET is_persistent = ? WHERE channel_id = ?",
                (1 if payload.persistent else 0, channel_id),
            )
        await get_db().commit()
        return {"channel_id": channel_id, "updated": True}

    async def delete_room(self, channel_id: int, guild_id: int, access_token: str) -> dict[str, Any]:
        await self._access_service.ensure_admin(access_token, str(guild_id))
        await self._discord.safe_bot_request("DELETE", f"/channels/{channel_id}")
        await get_db().execute("DELETE FROM voice_rooms WHERE channel_id = ?", (channel_id,))
        await get_db().commit()
        return {"channel_id": channel_id, "deleted": True}
