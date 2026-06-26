from __future__ import annotations

from typing import Dict, Optional

from core.domain.server_role_purpose import ServerRolePurpose
from core.interfaces.repositories import ServerRolePurposeRepositoryInterface
from infrastructure.database.connection import DatabaseManager
from infrastructure.database.repositories.base import BaseRepository
from infrastructure.logging import get_logger

logger = get_logger(__name__)


class ServerRolePurposeRepository(
    ServerRolePurposeRepositoryInterface,
    BaseRepository,
):
    _TABLE_NAME = "server_role_purposes"

    def __init__(self, db_manager: DatabaseManager):
        super().__init__(db_manager)

    async def set_role(
        self,
        guild_id: int,
        purpose: ServerRolePurpose,
        role_id: int,
    ) -> None:
        await self.execute(
            """
            INSERT INTO server_role_purposes (guild_id, purpose, role_id)
            VALUES (?, ?, ?)
            ON CONFLICT(guild_id, purpose) DO UPDATE SET
                role_id = excluded.role_id,
                updated_at = CURRENT_TIMESTAMP
            """,
            (guild_id, purpose.value, role_id),
        )
        await self.commit()
        logger.info(
            "Set server role purpose guild_id=%s purpose=%s role_id=%s",
            guild_id,
            purpose.value,
            role_id,
        )

    async def remove_role(
        self,
        guild_id: int,
        purpose: ServerRolePurpose,
    ) -> bool:
        cursor = await self.execute(
            """
            DELETE FROM server_role_purposes
            WHERE guild_id = ? AND purpose = ?
            """,
            (guild_id, purpose.value),
        )
        await self.commit()
        return bool(cursor.rowcount)

    async def get_role(
        self,
        guild_id: int,
        purpose: ServerRolePurpose,
    ) -> Optional[int]:
        row = await self.fetch_one(
            """
            SELECT role_id FROM server_role_purposes
            WHERE guild_id = ? AND purpose = ?
            """,
            (guild_id, purpose.value),
        )
        return int(row["role_id"]) if row else None

    async def get_all_roles(self, guild_id: int) -> Dict[str, int]:
        rows = await self.fetch_all(
            """
            SELECT purpose, role_id FROM server_role_purposes
            WHERE guild_id = ?
            """,
            (guild_id,),
        )
        return {row["purpose"]: int(row["role_id"]) for row in rows}
