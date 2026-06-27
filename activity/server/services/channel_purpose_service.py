from fastapi import HTTPException

from activity.server.dependencies import get_db
from activity.server.schemas.activity import ChannelPurposePayload
from activity.server.services.access_service import ActivityAccessService
from core.domain.channel_purpose import ChannelPurpose


class ChannelPurposeService:
    def __init__(self) -> None:
        self._access_service = ActivityAccessService()

    async def get_channel_purposes(self, guild_id: int, access_token: str) -> dict[str, int]:
        await self._access_service.ensure_panel_access(access_token, str(guild_id))
        rows = await get_db().fetch_all(
            "SELECT purpose, channel_id FROM server_channel_purposes WHERE guild_id = ?",
            (guild_id,),
        )
        return {row["purpose"]: int(row["channel_id"]) for row in rows}

    async def save_channel_purpose(self, payload: ChannelPurposePayload, access_token: str) -> dict[str, int]:
        await self._access_service.ensure_admin(access_token, str(payload.guild_id))
        await get_db().execute(
            """
            INSERT INTO server_channel_purposes (guild_id, purpose, channel_id)
            VALUES (?, ?, ?)
            ON CONFLICT(guild_id, purpose) DO UPDATE SET
                channel_id = excluded.channel_id,
                updated_at = CURRENT_TIMESTAMP
            """,
            (payload.guild_id, payload.purpose.value, payload.channel_id),
        )
        await get_db().commit()
        return await self.get_channel_purposes(payload.guild_id, access_token)

    async def get_required_purpose_channel(self, guild_id: int, purpose: ChannelPurpose) -> int:
        row = await get_db().fetch_one(
            """
            SELECT channel_id FROM server_channel_purposes
            WHERE guild_id = ? AND purpose = ?
            """,
            (guild_id, purpose.value),
        )
        if not row:
            raise HTTPException(
                status_code=400,
                detail=f"Channel purpose '{purpose.value}' is not configured",
            )
        return int(row["channel_id"])
