from application.schemas.server_role_purpose_schemas import ServerRolePurposeSchema
from activity.server.dependencies import get_role_purpose_service
from activity.server.schemas.activity import ActivityRolePayload
from activity.server.services.access_service import ActivityAccessService


class ActivityRoleService:
    def __init__(self) -> None:
        self._access_service = ActivityAccessService()

    async def get_roles(self, guild_id: int, access_token: str) -> dict[str, int]:
        await self._access_service.ensure_admin(access_token, str(guild_id))
        return await get_role_purpose_service().get_all_roles(guild_id)

    async def save_role(self, payload: ActivityRolePayload, access_token: str) -> dict[str, int]:
        await self._access_service.ensure_admin(access_token, str(payload.guild_id))
        validated = ServerRolePurposeSchema.model_validate(payload.model_dump())
        await get_role_purpose_service().set_role(
            validated.guild_id,
            validated.purpose,
            validated.role_id,
        )
        return await get_role_purpose_service().get_all_roles(validated.guild_id)
