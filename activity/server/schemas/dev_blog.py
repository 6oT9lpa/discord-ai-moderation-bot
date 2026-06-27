from typing import Literal, Optional

from pydantic import BaseModel, Field


class DevBlogEmbedPayload(BaseModel):
    title: Optional[str] = Field(default=None, max_length=256)
    description: str = Field(min_length=1, max_length=4096)
    image_url: Optional[str] = Field(default=None, max_length=2048)
    color: int = Field(default=0x5865F2, ge=0, le=0xFFFFFF)


class DevBlogPostPayload(BaseModel):
    guild_id: int = Field(gt=0)
    title: str = Field(min_length=1, max_length=256)
    content: Optional[str] = Field(default=None, max_length=2000)
    embeds: list[DevBlogEmbedPayload] = Field(min_length=1, max_length=10)
    status: Literal["draft", "published"] = "published"
