from typing import Optional

from pydantic import BaseModel


class WelcomeConfigPayload(BaseModel):
    guild_id: int
    title: Optional[str] = None
    description: Optional[str] = None
    thumbnail_url: Optional[str] = None
    footer_text: Optional[str] = None
    footer_icon_url: Optional[str] = None
    color: Optional[int] = None
    is_enabled: bool = True
    rules_channel_id: Optional[int] = None
    roles_channel_id: Optional[int] = None
