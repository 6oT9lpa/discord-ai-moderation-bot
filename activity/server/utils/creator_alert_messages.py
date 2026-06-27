from typing import Any

from activity.server.schemas.creator_alerts import CreatorAlertTestPayload


def build_creator_alert_message(payload: CreatorAlertTestPayload) -> dict[str, Any]:
    title = {
        "twitch": "Stream is live",
        "youtube": "New video published",
        "kick": "Kick stream is live",
    }[payload.platform]
    template = payload.template or "{creator} is active on {platform}: {url}"
    description = template.format(
        creator=payload.channel_name,
        platform=payload.platform.title(),
        url=payload.channel_url,
    )
    content = f"<@&{payload.ping_role_id}>" if payload.ping_role_id else ""
    return {
        "content": content,
        "embeds": [
            {
                "title": title,
                "description": description,
                "url": payload.channel_url,
                "color": 0x5865F2,
            }
        ],
        "allowed_mentions": {"roles": [str(payload.ping_role_id)] if payload.ping_role_id else []},
    }
