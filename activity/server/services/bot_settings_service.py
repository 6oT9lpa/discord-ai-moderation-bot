from typing import Any

from activity.server.services.access_service import ActivityAccessService
from activity.server.services.channel_purpose_service import ChannelPurposeService
from infrastructure.config import get_config


class BotSettingsService:
    def __init__(self) -> None:
        self._access_service = ActivityAccessService()
        self._channel_purpose_service = ChannelPurposeService()

    async def get_settings(self, guild_id: int, access_token: str) -> dict[str, Any]:
        await self._access_service.ensure_admin(access_token, str(guild_id))
        config = get_config()
        return {
            "guild_id": guild_id,
            "command_prefix": config.command_prefix,
            "activity_name": config.activity_name,
            "bot_status": config.bot_status,
            "activity_rotation_enabled": config.activity_rotation_enabled,
            "activity_rotation_interval_seconds": config.activity_rotation_interval_seconds,
            "log_level": config.log_level,
            "retention": {
                "message_log_retention_days": config.message_log_retention_days,
                "punishment_retention_days": config.punishment_retention_days,
            },
            "channel_purposes": await self._channel_purpose_service.get_channel_purposes(guild_id, access_token),
        }
