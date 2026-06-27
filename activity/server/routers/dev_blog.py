from typing import Any

from fastapi import APIRouter, Depends, Query

from activity.server.dependencies import require_bearer_token
from activity.server.schemas.dev_blog import DevBlogPostPayload
from activity.server.services.dev_blog_service import DevBlogService

router = APIRouter()
service = DevBlogService()


@router.get("/api/dev-blog/posts")
async def list_dev_blog_posts(
    guild_id: int = Query(gt=0),
    limit: int = Query(default=25, ge=1, le=100),
    access_token: str = Depends(require_bearer_token),
) -> list[dict[str, Any]]:
    return await service.list_posts(guild_id, limit, access_token)


@router.post("/api/dev-blog/posts")
async def create_dev_blog_post(
    payload: DevBlogPostPayload,
    access_token: str = Depends(require_bearer_token),
) -> dict[str, Any]:
    return await service.create_post(payload, access_token)
