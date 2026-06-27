from typing import Any

from activity.server.dependencies import get_db
from activity.server.schemas.welcome import WelcomeConfigPayload
from activity.server.services.access_service import ActivityAccessService
from activity.server.utils.welcome_config import normalize_config


class ActivityWelcomeService:
    def __init__(self) -> None:
        self._access_service = ActivityAccessService()

    async def get_config(self, guild_id: int, access_token: str) -> dict[str, Any]:
        await self._access_service.ensure_admin(access_token, str(guild_id))
        config = await get_db().fetch_one(
            "SELECT * FROM welcome_config WHERE guild_id = ?",
            (guild_id,),
        )
        return normalize_config(config, guild_id)

    async def save_config(self, payload: WelcomeConfigPayload, access_token: str) -> dict[str, Any]:
        await self._access_service.ensure_admin(access_token, str(payload.guild_id))
        db = get_db()
        values = (
            payload.guild_id,
            payload.title,
            payload.description,
            payload.thumbnail_url,
            payload.footer_text,
            payload.footer_icon_url,
            payload.color,
            1 if payload.is_enabled else 0,
            payload.rules_channel_id,
            payload.roles_channel_id,
        )
        await db.execute(
            """
            INSERT INTO welcome_config (
                guild_id, title, description, thumbnail_url, footer_text,
                footer_icon_url, color, is_enabled, rules_channel_id, roles_channel_id
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(guild_id) DO UPDATE SET
                title = excluded.title,
                description = excluded.description,
                thumbnail_url = excluded.thumbnail_url,
                footer_text = excluded.footer_text,
                footer_icon_url = excluded.footer_icon_url,
                color = excluded.color,
                is_enabled = excluded.is_enabled,
                rules_channel_id = excluded.rules_channel_id,
                roles_channel_id = excluded.roles_channel_id,
                updated_at = CURRENT_TIMESTAMP
            """,
            values,
        )
        await db.commit()
        saved = await db.fetch_one(
            "SELECT * FROM welcome_config WHERE guild_id = ?",
            (payload.guild_id,),
        )
        return normalize_config(saved, payload.guild_id)

    async def reset_config(self, guild_id: int, access_token: str) -> dict[str, Any]:
        await self._access_service.ensure_admin(access_token, str(guild_id))
        db = get_db()
        await db.execute("DELETE FROM welcome_config WHERE guild_id = ?", (guild_id,))
        await db.commit()
        return normalize_config(None, guild_id)
