from __future__ import annotations

from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta, timezone

from infrastructure.database.connection import DatabaseManager
from infrastructure.database.repositories.base import BaseRepository
from infrastructure.logging.logger import get_logger

logger = get_logger(__name__)

MSK = timezone(timedelta(hours=3))


def get_msk_timestamp() -> str:
    """Получить текущий timestamp в МСК"""
    return datetime.now(MSK).strftime("%Y-%m-%dT%H:%M:%S")


class StatsRepository(BaseRepository):
    """
    Репозиторий для хранения статистики пользователей: сообщения, время в голосе, предупреждения и т.д.
    """
    _TABLE_NAME = "user_stats"

    def __init__(self, db_manager: DatabaseManager):
        super().__init__(db_manager)

    async def get_or_create(self, user_id: int, guild_id: int) -> bool:
        """Создать запись пользователя, если её нет"""
        check_query = "SELECT user_id FROM user_stats WHERE guild_id = ? AND user_id = ?"
        result = await self.fetch_one(check_query, (guild_id, user_id))
        
        if result:
            return True
        
        insert_query = """
            INSERT INTO user_stats 
                (user_id, guild_id, messages_count, voice_minutes, warnings_count, joined_at)
            VALUES (?, ?, 0, 0, 0, ?)
        """
        try:
            await self.execute(insert_query, (user_id, guild_id, get_msk_timestamp()))
            await self.commit()
            return True
        except Exception as e:
            logger.error(f"Failed to create user {user_id}: {e}")
            return False

    async def increment_messages(self, user_id: int, guild_id: int) -> None:
        """Увеличить счётчик сообщений на 1"""
        await self.get_or_create(user_id, guild_id)
        
        query = """
            UPDATE user_stats 
            SET messages_count = messages_count + 1,
                last_message = ?,
                updated_at = ?
            WHERE guild_id = ? AND user_id = ?
        """
        now = get_msk_timestamp()
        await self.execute(query, (now, now, guild_id, user_id))
        await self.commit()

    async def add_voice_minutes(self, user_id: int, guild_id: int, minutes: int) -> None:
        """Добавить минуты в голосовом канале"""
        if minutes <= 0:
            return

        await self.get_or_create(user_id, guild_id)
        
        query = """
            UPDATE user_stats 
            SET voice_minutes = voice_minutes + ?,
                updated_at = ?
            WHERE guild_id = ? AND user_id = ?
        """
        await self.execute(query, (minutes, get_msk_timestamp(), guild_id, user_id))
        await self.commit()

    async def increment_warnings(self, user_id: int, guild_id: int) -> None:
        """Увеличить счётчик предупреждений"""
        await self.get_or_create(user_id, guild_id)
        
        query = """
            UPDATE user_stats 
            SET warnings_count = warnings_count + 1,
                updated_at = ?
            WHERE guild_id = ? AND user_id = ?
        """
        await self.execute(query, (get_msk_timestamp(), guild_id, user_id))
        await self.commit()

    async def log_message_to_history(self, message_id: int, user_id: int, guild_id: int, channel_id: int) -> None:
        """Сохранить сообщение в историю"""
        query = """
            INSERT OR IGNORE INTO messages (id, user_id, guild_id, channel_id, timestamp)
            VALUES (?, ?, ?, ?, ?)
        """
        now = get_msk_timestamp()
        try:
            await self.execute(query, (message_id, user_id, guild_id, channel_id, now))
            await self.commit()
        except Exception as e:
            logger.error(f"Failed to log message to history: {e}")

    async def get_user_stats(self, user_id: int, guild_id: int) -> Optional[Dict[str, Any]]:
        """Получить статистику пользователя"""
        query = """
            SELECT user_id, messages_count, voice_minutes, warnings_count,
                   joined_at, last_message
            FROM user_stats
            WHERE guild_id = ? AND user_id = ?
        """
        return await self.fetch_one(query, (guild_id, user_id))

    async def get_top_users(self, guild_id: int, limit: int = 10, sort_by: str = "messages_count") -> List[Dict[str, Any]]:
        """Получить топ пользователей по активности"""
        allowed_sort = {"messages_count", "voice_minutes", "warnings_count"}
        if sort_by not in allowed_sort:
            raise ValueError(f"Нельзя сортировать по: {sort_by}")

        query = f"""
            SELECT user_id, {sort_by}
            FROM user_stats
            WHERE guild_id = ? AND {sort_by} > 0
            ORDER BY {sort_by} DESC
            LIMIT ?
        """
        return await self.fetch_all(query, (guild_id, limit))

    async def get_all_stats(self, guild_id: int) -> List[Dict[str, Any]]:
        """Получить всю статистику пользователей сервера"""
        query = """
            SELECT user_id, messages_count, voice_minutes, warnings_count,
                   joined_at, last_message
            FROM user_stats
            WHERE guild_id = ?
            ORDER BY messages_count DESC
        """
        return await self.fetch_all(query, (guild_id,))

    async def get_activity_summary(self, guild_id: int) -> Dict[str, Any]:
        """Получить сводку по активности сервера"""
        query = """
            SELECT
                COUNT(*) as total_members,
                SUM(messages_count) as total_messages,
                SUM(voice_minutes) as total_voice_minutes,
                SUM(warnings_count) as total_warnings
            FROM user_stats
            WHERE guild_id = ?
        """
        row = await self.fetch_one(query, (guild_id,))
        return {
            "total_members": row["total_members"] or 0,
            "total_messages": row["total_messages"] or 0,
            "total_voice_minutes": row["total_voice_minutes"] or 0,
            "total_warnings": row["total_warnings"] or 0,
        }

    async def reset_user_stats(self, user_id: int, guild_id: int) -> bool:
        """Сбросить статистику пользователя"""
        query = """
            UPDATE user_stats
            SET messages_count = 0,
                voice_minutes = 0,
                warnings_count = 0,
                last_message = NULL,
                updated_at = ?
            WHERE guild_id = ? AND user_id = ?
        """
        cursor = await self.execute(query, (get_msk_timestamp(), guild_id, user_id))
        await self.commit()
        return cursor.rowcount > 0

    async def delete_user_stats(self, user_id: int, guild_id: int) -> bool:
        """Удалить запись пользователя из статистики"""
        query = "DELETE FROM user_stats WHERE guild_id = ? AND user_id = ?"
        cursor = await self.execute(query, (guild_id, user_id))
        await self.commit()
        return cursor.rowcount > 0

    async def get_top_channels(self, guild_id: int, days: int = 7, limit: int = 5) -> List[Dict[str, Any]]:
        """Получить топ-каналов по активности"""
        cutoff = datetime.now(MSK) - timedelta(days=days)
        query = """
            SELECT channel_id, COUNT(*) as count
            FROM messages
            WHERE guild_id = ? AND timestamp >= ? AND deleted = 0
            GROUP BY channel_id
            ORDER BY count DESC
            LIMIT ?
        """
        return await self.fetch_all(query, (guild_id, cutoff.strftime("%Y-%m-%dT%H:%M:%S"), limit))

    async def get_activity_by_hour(self, guild_id: int, days: int = 7) -> List[Dict[str, Any]]:
        """Получить активность по часам (МСК)"""
        cutoff = datetime.now(MSK) - timedelta(days=days)
        query = """
            SELECT CAST(substr(timestamp, 12, 2) AS INTEGER) as hour, COUNT(*) as count
            FROM messages
            WHERE guild_id = ? AND timestamp >= ? AND deleted = 0
            GROUP BY hour
            ORDER BY hour
        """
        return await self.fetch_all(query, (guild_id, cutoff.strftime("%Y-%m-%dT%H:%M:%S")))

    async def get_leaderboard(self, guild_id: int, days: int = 7, limit: int = 10) -> List[Dict[str, Any]]:
        """Получить топ-участников по сообщениям"""
        cutoff = datetime.now(MSK) - timedelta(days=days)
        query = """
            SELECT user_id, COUNT(*) as count
            FROM messages
            WHERE guild_id = ? AND timestamp >= ? AND deleted = 0
            GROUP BY user_id
            ORDER BY count DESC
            LIMIT ?
        """
        return await self.fetch_all(query, (guild_id, cutoff.strftime("%Y-%m-%dT%H:%M:%S"), limit))