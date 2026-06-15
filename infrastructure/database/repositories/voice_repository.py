from __future__ import annotations

from typing import List, Optional, Dict, Any
from datetime import datetime, timezone, timedelta

from infrastructure.database.connection import DatabaseManager
from infrastructure.database.repositories.base import BaseRepository
from infrastructure.logging.logger import get_logger

logger = get_logger(__name__)

MSK = timezone(timedelta(hours=3))


class VoiceRepository(BaseRepository):
    """Репозиторий для управления временными голосовыми комнатами"""
    
    _TABLE_NAME = "voice_rooms"

    def __init__(self, db_manager: DatabaseManager):
        super().__init__(db_manager)

    async def create(self, channel_id: int, guild_id: int, owner_id: int, name: str) -> bool:
        query = """
            INSERT INTO voice_rooms (channel_id, guild_id, owner_id, name, created_at)
            VALUES (?, ?, ?, ?, ?)
        """
        now = datetime.now(MSK).isoformat()
        try:
            await self.execute(query, (channel_id, guild_id, owner_id, name, now))
            await self.commit()
            return True
        except Exception as e:
            logger.error(f"Failed to create voice room: {e}")
            return False

    async def delete(self, channel_id: int) -> bool:
        query = "DELETE FROM voice_rooms WHERE channel_id = ?"
        try:
            await self.execute(query, (channel_id,))
            await self.commit()
            return True
        except Exception as e:
            logger.error(f"Failed to delete voice room: {e}")
            return False

    async def get(self, channel_id: int) -> Optional[Dict[str, Any]]:
        query = "SELECT * FROM voice_rooms WHERE channel_id = ?"
        return await self.fetch_one(query, (channel_id,))

    async def get_by_owner(self, user_id: int, guild_id: int) -> Optional[Dict[str, Any]]:
        query = "SELECT * FROM voice_rooms WHERE owner_id = ? AND guild_id = ?"
        return await self.fetch_one(query, (user_id, guild_id))

    async def get_all(self, guild_id: int) -> List[Dict[str, Any]]:
        query = "SELECT * FROM voice_rooms WHERE guild_id = ?"
        return await self.fetch_all(query, (guild_id,))

    async def update_owner(self, channel_id: int, new_owner_id: int) -> bool:
        query = "UPDATE voice_rooms SET owner_id = ? WHERE channel_id = ?"
        try:
            await self.execute(query, (new_owner_id, channel_id))
            await self.commit()
            return True
        except Exception as e:
            logger.error(f"Failed to update owner: {e}")
            return False

    async def set_persistent(self, channel_id: int, persistent: bool = True) -> bool:
        query = "UPDATE voice_rooms SET is_persistent = ? WHERE channel_id = ?"
        try:
            await self.execute(query, (int(persistent), channel_id))
            await self.commit()
            return True
        except:
            return False

    async def set_config(self, key: str, value: str) -> bool:
        query = "INSERT OR REPLACE INTO voice_config (key, value) VALUES (?, ?)"
        try:
            await self.execute(query, (key, value))
            await self.commit()
            return True
        except:
            return False

    async def get_config(self, key: str) -> Optional[str]:
        query = "SELECT value FROM voice_config WHERE key = ?"
        row = await self.fetch_one(query, (key,))
        return row["value"] if row else None