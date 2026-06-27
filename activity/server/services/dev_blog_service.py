import json
from typing import Any, Optional

from activity.server.dependencies import get_db
from activity.server.schemas.dev_blog import DevBlogPostPayload
from activity.server.services.access_service import ActivityAccessService
from activity.server.services.channel_purpose_service import ChannelPurposeService
from activity.server.services.discord_service import DiscordService
from activity.server.utils.dev_blog_messages import build_dev_blog_message
from core.domain.channel_purpose import ChannelPurpose


class DevBlogService:
    def __init__(self) -> None:
        self._access_service = ActivityAccessService()
        self._channel_purpose_service = ChannelPurposeService()
        self._discord = DiscordService()

    async def list_posts(self, guild_id: int, limit: int, access_token: str) -> list[dict[str, Any]]:
        await self._access_service.ensure_developer_or_admin(access_token, str(guild_id))
        return await get_db().fetch_all(
            """
            SELECT id, guild_id, channel_id, message_id, author_id, title,
                   payload_json, status, created_at, updated_at
            FROM dev_blog_posts
            WHERE guild_id = ?
            ORDER BY created_at DESC, id DESC
            LIMIT ?
            """,
            (guild_id, limit),
        )

    async def create_post(self, payload: DevBlogPostPayload, access_token: str) -> dict[str, Any]:
        user, _ = await self._access_service.ensure_developer_or_admin(access_token, str(payload.guild_id))
        channel_id = await self._channel_purpose_service.get_required_purpose_channel(payload.guild_id, ChannelPurpose.DEV_BLOG)
        message_payload = build_dev_blog_message(payload)
        message_id: Optional[int] = None

        if payload.status == "published":
            message = await self._discord.bot_request(
                "POST",
                f"/channels/{channel_id}/messages",
                json_body=message_payload,
            )
            message_id = int(message["id"])

        await get_db().execute(
            """
            INSERT INTO dev_blog_posts (
                guild_id, channel_id, message_id, author_id, title, payload_json, status
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                payload.guild_id,
                channel_id,
                message_id,
                int(user["id"]),
                payload.title,
                json.dumps(message_payload, ensure_ascii=False),
                payload.status,
            ),
        )
        await get_db().commit()
        row = await get_db().fetch_one("SELECT last_insert_rowid() AS id")
        return {
            "id": int(row["id"]),
            "channel_id": channel_id,
            "message_id": message_id,
            "status": payload.status,
            "payload": message_payload,
        }
