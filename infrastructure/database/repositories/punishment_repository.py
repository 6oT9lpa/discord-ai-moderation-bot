from typing import List, Dict, Any, Optional
from datetime import datetime

from infrastructure.database.repositories.base import BaseRepository


class PunishmentRepository(BaseRepository):
    _TABLE_NAME = "punishments"
    _ALLOWED_COLUMNS = {
        "id", "user_id", "mod_id", "type", "reason", 
        "duration", "expires_at", "active", "timestamp"
    }

    async def create_punishment(
        self,
        user_id: int,
        mod_id: Optional[int],
        punishment_type: str,
        reason: Optional[str] = None,
        duration: Optional[str] = None,
        expires_at: Optional[datetime] = None
    ) -> int:
        """
        Создать новое наказание
        
        Args:
            user_id: ID пользователя
            mod_id: ID модератора/администратора
            punishment_type: Тип наказания (warn, mute, kick, ban)
            reason: Причина наказания
            duration: Длительность наказания ('10m', '1h', '1d')
            expires_at: Дата истечения наказания
            
        Returns:
            ID созданного наказания
        """
        data = {
            "user_id": user_id,
            "mod_id": mod_id,
            "type": punishment_type,
            "reason": reason,
            "duration": duration,
            "expires_at": expires_at,
            "active": 1,
            "timestamp": datetime.now()
        }
        return await self.insert(data)

    async def get_user_violations(self, user_id: int, active_only: bool = False) -> List[Dict[str, Any]]:
        """
        Получить все нарушения пользователя
        
        Args:
            user_id: ID пользователя
            active_only: Только активные наказания
            
        Returns:
            Список нарушений
        """
        if active_only:
            query = f"""
                SELECT * FROM {self._TABLE_NAME}
                WHERE user_id = ? AND active = 1
                ORDER BY timestamp DESC
            """
        else:
            query = f"""
                SELECT * FROM {self._TABLE_NAME}
                WHERE user_id = ?
                ORDER BY timestamp DESC
            """
        
        return await self.fetch_all(query, (user_id,))

    async def get_violation_count(self, user_id: int, active_only: bool = False) -> int:
        """
        Получить количество нарушений пользователя
        
        Args:
            user_id: ID пользователя
            active_only: Только активные наказания
            
        Returns:
            Количество нарушений
        """
        if active_only:
            query = f"""
                SELECT COUNT(*) as count FROM {self._TABLE_NAME}
                WHERE user_id = ? AND active = 1
            """
        else:
            query = f"""
                SELECT COUNT(*) as count FROM {self._TABLE_NAME}
                WHERE user_id = ?
            """
        
        result = await self.fetch_one(query, (user_id,))
        return result["count"] if result else 0

    async def get_violations_by_type(self, user_id: int, punishment_type: str) -> List[Dict[str, Any]]:
        """
        Получить нарушения пользователя определённого типа
        
        Args:
            user_id: ID пользователя
            punishment_type: Тип наказания
            
        Returns:
            Список нарушений
        """
        query = f"""
            SELECT * FROM {self._TABLE_NAME}
            WHERE user_id = ? AND type = ?
            ORDER BY timestamp DESC
        """
        
        return await self.fetch_all(query, (user_id, punishment_type))

    async def deactivate_punishment(self, punishment_id: int) -> None:
        """
        Деактивировать наказание (размут, разбан и т.д.)
        
        Args:
            punishment_id: ID наказания
        """
        query = f"""
            UPDATE {self._TABLE_NAME}
            SET active = 0
            WHERE id = ?
        """
        
        await self.execute(query, (punishment_id,))
        await self.commit()

    async def get_recent_punishments(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Получить недавние наказания
        
        Args:
            limit: Максимальное количество наказаний
            
        Returns:
            Список наказаний
        """
        query = f"""
            SELECT * FROM {self._TABLE_NAME}
            ORDER BY timestamp DESC
            LIMIT ?
        """
        
        return await self.fetch_all(query, (limit,))

    async def count_active_punishments_by_type(self, user_id: int) -> Dict[str, int]:
        """
        Получить количество активных наказаний по типам
        
        Args:
            user_id: ID пользователя
            
        Returns:
            Словарь с типами наказаний и их количеством
        """
        query = f"""
            SELECT type, COUNT(*) as count FROM {self._TABLE_NAME}
            WHERE user_id = ? AND active = 1
            GROUP BY type
        """
        
        results = await self.fetch_all(query, (user_id,))
        return {row["type"]: row["count"] for row in results}
