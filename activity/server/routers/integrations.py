from typing import Any

from fastapi import APIRouter, Depends, Query

from activity.server.dependencies import require_bearer_token
from activity.server.services.integrations_service import IntegrationsService

router = APIRouter()
service = IntegrationsService()


@router.get("/api/integrations")
async def get_integrations(
    guild_id: int = Query(gt=0),
    access_token: str = Depends(require_bearer_token),
) -> dict[str, Any]:
    return await service.get_integrations(guild_id, access_token)
