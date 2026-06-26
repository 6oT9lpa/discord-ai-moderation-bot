from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Dict, Optional

from core.domain.server_role_purpose import ServerRolePurpose


class ServerRolePurposeServiceInterface(ABC):
    @abstractmethod
    async def set_role(
        self,
        guild_id: int,
        purpose: ServerRolePurpose,
        role_id: int,
    ) -> None:
        pass

    @abstractmethod
    async def remove_role(
        self,
        guild_id: int,
        purpose: ServerRolePurpose,
    ) -> bool:
        pass

    @abstractmethod
    async def get_role(
        self,
        guild_id: int,
        purpose: ServerRolePurpose,
    ) -> Optional[int]:
        pass

    @abstractmethod
    async def get_all_roles(self, guild_id: int) -> Dict[str, int]:
        pass
