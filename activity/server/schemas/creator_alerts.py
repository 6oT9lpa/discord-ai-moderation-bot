from typing import Literal, Optional

from pydantic import BaseModel, Field


class CreatorAlertSourcePayload(BaseModel):
    guild_id: int = Field(gt=0)
    platform: Literal["twitch", "youtube", "kick"]
    channel_url: str = Field(min_length=1, max_length=2048)
    channel_name: Optional[str] = Field(default=None, max_length=120)
    template: Optional[str] = Field(default=None, max_length=2000)
    ping_role_id: Optional[int] = Field(default=None, gt=0)
    active: bool = True
    user_id: Optional[int] = Field(default=None, gt=0)


class CreatorAlertTestPayload(BaseModel):
    guild_id: int = Field(gt=0)
    platform: Literal["twitch", "youtube", "kick"]
    channel_name: str = Field(min_length=1, max_length=120)
    channel_url: str = Field(min_length=1, max_length=2048)
    template: Optional[str] = Field(default=None, max_length=2000)
    ping_role_id: Optional[int] = Field(default=None, gt=0)
