from fastapi import APIRouter, Depends, Query

from activity.server.dependencies import require_bearer_token
from activity.server.schemas.activity import ActivityRolePayload
from activity.server.services.activity_role_service import ActivityRoleService

router = APIRouter()
service = ActivityRoleService()


@router.get("/api/activity/roles")
async def get_activity_roles(
    guild_id: int = Query(gt=0),
    access_token: str = Depends(require_bearer_token),
) -> dict[str, int]:
    return await service.get_roles(guild_id, access_token)


@router.put("/api/activity/roles")
async def save_activity_role(
    payload: ActivityRolePayload,
    access_token: str = Depends(require_bearer_token),
) -> dict[str, int]:
    return await service.save_role(payload, access_token)
