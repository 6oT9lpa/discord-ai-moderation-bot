from fastapi import APIRouter, Depends, Query

from activity.server.dependencies import require_bearer_token
from activity.server.schemas.activity import ActivitySession
from activity.server.services.session_service import ActivitySessionService

router = APIRouter()
service = ActivitySessionService()


@router.get("/api/activity/session", response_model=ActivitySession)
async def get_activity_session(
    guild_id: str = Query(min_length=1),
    access_token: str = Depends(require_bearer_token),
) -> ActivitySession:
    return await service.get_session(guild_id, access_token)
