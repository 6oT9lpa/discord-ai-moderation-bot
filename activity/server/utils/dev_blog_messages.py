from datetime import datetime, timezone
from typing import Any

from activity.server.schemas.dev_blog import DevBlogPostPayload


def build_dev_blog_message(payload: DevBlogPostPayload) -> dict[str, Any]:
    return {
        "content": payload.content or "",
        "embeds": [
            {
                "title": embed.title or payload.title,
                "description": embed.description,
                "color": embed.color,
                **({"image": {"url": embed.image_url}} if embed.image_url else {}),
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
            for embed in payload.embeds
        ],
        "allowed_mentions": {"parse": []},
    }
