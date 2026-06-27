from typing import Any

import httpx
from fastapi import HTTPException

from activity.server.config import activity_server_config
from activity.server.dependencies import get_role_purpose_service
from activity.server.services.discord_service import DiscordService
from core.domain.server_role_purpose import ServerRolePurpose


class ActivityAccessService:
    def __init__(self) -> None:
        self._discord = DiscordService()

    async def fetch_user_and_access_state(self, access_token: str, guild_id: str) -> tuple[dict[str, Any], dict[str, bool]]:
        headers = {"Authorization": f"Bearer {access_token}"}
        async with httpx.AsyncClient(timeout=10) as client:
            user_response = await client.get(f"{activity_server_config.discord_api_base}/users/@me", headers=headers)
            guilds_response = await client.get(f"{activity_server_config.discord_api_base}/users/@me/guilds", headers=headers)

        if user_response.status_code >= 400:
            raise HTTPException(status_code=user_response.status_code, detail=user_response.text)
        if guilds_response.status_code >= 400:
            raise HTTPException(status_code=guilds_response.status_code, detail=guilds_response.text)

        user = user_response.json()
        guilds = guilds_response.json()
        current_guild = next((guild for guild in guilds if guild.get("id") == guild_id), None)
        if current_guild is None:
            raise HTTPException(status_code=403, detail="User is not a member of this guild")

        permissions = int(current_guild.get("permissions") or 0)
        member_role_ids = await self._discord.fetch_member_role_ids(guild_id, user["id"])
        role_purposes = await get_role_purpose_service().get_all_roles(int(guild_id))

        admin_role_id = role_purposes.get(ServerRolePurpose.ACTIVITY_ADMIN.value)
        streamer_role_id = role_purposes.get(ServerRolePurpose.ACTIVITY_STREAMER.value)
        developer_role_id = role_purposes.get(ServerRolePurpose.ACTIVITY_DEVELOPER.value)

        access = {
            "is_admin": bool(permissions & activity_server_config.administrator_permission)
            or bool(admin_role_id and admin_role_id in member_role_ids),
            "is_streamer": bool(streamer_role_id and streamer_role_id in member_role_ids),
            "is_developer": bool(developer_role_id and developer_role_id in member_role_ids),
        }

        return user, access

    async def ensure_admin(self, access_token: str, guild_id: str) -> None:
        _, access = await self.fetch_user_and_access_state(access_token, guild_id)
        if not access["is_admin"]:
            raise HTTPException(status_code=403, detail="Administrator permission is required")

    async def ensure_panel_access(self, access_token: str, guild_id: str) -> tuple[dict[str, Any], dict[str, bool]]:
        user, access = await self.fetch_user_and_access_state(access_token, guild_id)
        if not (access["is_admin"] or access["is_streamer"] or access["is_developer"]):
            raise HTTPException(status_code=403, detail="Activity module access is required")
        return user, access

    async def ensure_developer_or_admin(self, access_token: str, guild_id: str) -> tuple[dict[str, Any], dict[str, bool]]:
        user, access = await self.fetch_user_and_access_state(access_token, guild_id)
        if not (access["is_admin"] or access["is_developer"]):
            raise HTTPException(status_code=403, detail="Developer or administrator access is required")
        return user, access
