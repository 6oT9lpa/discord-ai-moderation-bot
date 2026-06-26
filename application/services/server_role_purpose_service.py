from __future__ import annotations

from typing import Dict, Optional

from core.domain.server_role_purpose import ServerRolePurpose
from core.interfaces.repositories import ServerRolePurposeRepositoryInterface
from core.interfaces.services import ServerRolePurposeServiceInterface
from infrastructure.logging import get_logger

logger = get_logger(__name__)


class ServerRolePurposeService(ServerRolePurposeServiceInterface):
    def __init__(self, repository: ServerRolePurposeRepositoryInterface):
        self._repository = repository

    async def set_role(
        self,
        guild_id: int,
        purpose: ServerRolePurpose,
        role_id: int,
    ) -> None:
        await self._repository.set_role(guild_id, purpose, role_id)
        logger.info(
            "Server role purpose updated guild_id=%s purpose=%s role_id=%s",
            guild_id,
            purpose.value,
            role_id,
        )

    async def remove_role(
        self,
        guild_id: int,
        purpose: ServerRolePurpose,
    ) -> bool:
        return await self._repository.remove_role(guild_id, purpose)

    async def get_role(
        self,
        guild_id: int,
        purpose: ServerRolePurpose,
    ) -> Optional[int]:
        return await self._repository.get_role(guild_id, purpose)

    async def get_all_roles(self, guild_id: int) -> Dict[str, int]:
        return await self._repository.get_all_roles(guild_id)
