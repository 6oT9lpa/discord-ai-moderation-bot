from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import List, Dict, Optional, Any
import disnake

from infrastructure.database.repositories.stats_repository import StatsRepository
from infrastructure.logging import get_logger
from infrastructure.config import BotConfig

logger = get_logger(__name__)

MSK = timezone(timedelta(hours=3))


class StatsService:
    """
    Сервис для сбора и предоставления статистики по серверу и участникам.
    """

    def __init__(self, stats_repo: StatsRepository, config: BotConfig):
        self.stats_repo = stats_repo
        self._config = config
        self._bot: Optional[disnake.Client] = None

    def set_bot(self, bot: disnake.Client) -> None:
        """Установить ссылку на бота"""
        self._bot = bot

    async def log_message(self, message: disnake.Message) -> None:
        """Залогировать сообщение: участник + сервер"""
        if message.author.bot or not message.guild:
            return

        try:
            await self.stats_repo.get_or_create(message.author.id, message.guild.id)
            await self.stats_repo.increment_messages(message.author.id, message.guild.id)
            await self.stats_repo.log_message_to_history(
                message.id, message.author.id, message.guild.id, message.channel.id
            )
        except Exception as e:
            logger.error(f"Error logging message: {e}")

    async def log_voice_activity(self, member: disnake.Member, joined_at: datetime) -> None:
        """Залогировать время в голосе (в минутах)"""
        if member.bot or not member.guild:
            return

        duration = datetime.now(MSK) - joined_at
        minutes = int(duration.total_seconds() // 60)
        if minutes <= 0:
            return

        try:
            await self.stats_repo.get_or_create(member.id, member.guild.id)
            await self.stats_repo.add_voice_minutes(member.id, member.guild.id, minutes)
        except Exception as e:
            logger.error(f"Error logging voice activity for {member.id}: {e}")

    async def log_member_join(self) -> None:
        """Залогировать вход участника"""
        pass

    async def log_member_leave(self) -> None:
        """Залогировать выход участника"""
        pass

    async def ensure_user_exists(self, user_id: int, guild_id: int) -> bool:
        """Гарантировать, что пользователь есть в статистике"""
        try:
            return await self.stats_repo.get_or_create(user_id, guild_id)
        except Exception as e:
            logger.error(f"Error ensuring user exists: {e}")
            return False

    async def get_user_stats(self, user_id: int, guild_id: int) -> Optional[Dict[str, Any]]:
        """Получить статистику пользователя"""
        return await self.stats_repo.get_user_stats(user_id, guild_id)

    async def get_top_channels(self, guild_id: int, days: int = 7, limit: int = 5) -> List[Dict[str, Any]]:
        """Получить топ-каналов по активности"""
        return await self.stats_repo.get_top_channels(guild_id, days, limit)

    async def get_activity_by_hour(self, guild_id: int, days: int = 7) -> List[Dict[str, int]]:
        """Получить активность по часам (0–23)"""
        rows = await self.stats_repo.get_activity_by_hour(guild_id, days)
        result = {str(h).zfill(2): 0 for h in range(24)}
        for row in rows:
            hour = str(row["hour"]).zfill(2)
            result[hour] = row["count"]
        return [{"hour": h, "count": c} for h, c in result.items()]

    async def get_leaderboard(self, guild_id: int, days: int = 7, limit: int = 10) -> List[Dict[str, Any]]:
        """Получить топ-участников по сообщениям за N дней"""
        return await self.stats_repo.get_leaderboard(guild_id, days, limit)

    async def get_server_stats(self, guild_id: int, period: int = 7) -> Dict[str, Any]:
        """Получить общую статистику сервера за период"""
        cutoff = datetime.now(MSK) - timedelta(days=period)
        cutoff_str = cutoff.strftime("%Y-%m-%dT%H:%M:%S")
        
        # Основная статистика из messages
        query = """
            SELECT 
                COUNT(*) as total_messages,
                COUNT(DISTINCT user_id) as active_users,
                COUNT(DISTINCT channel_id) as active_channels
            FROM messages
            WHERE guild_id = ? AND timestamp >= ? AND deleted = 0
        """
        row = await self.stats_repo.fetch_one(query, (guild_id, cutoff_str))
        
        # Самый активный пользователь
        top_user_query = """
            SELECT user_id, COUNT(*) as count
            FROM messages
            WHERE guild_id = ? AND timestamp >= ? AND deleted = 0
            GROUP BY user_id
            ORDER BY count DESC
            LIMIT 1
        """
        top_user = await self.stats_repo.fetch_one(top_user_query, (guild_id, cutoff_str))
        
        # Самый активный канал
        top_channel_query = """
            SELECT channel_id, COUNT(*) as count
            FROM messages
            WHERE guild_id = ? AND timestamp >= ? AND deleted = 0
            GROUP BY channel_id
            ORDER BY count DESC
            LIMIT 1
        """
        top_channel = await self.stats_repo.fetch_one(top_channel_query, (guild_id, cutoff_str))
        
        # Самый активный час
        top_hour_query = """
            SELECT CAST(substr(timestamp, 12, 2) AS INTEGER) as hour, COUNT(*) as count
            FROM messages
            WHERE guild_id = ? AND timestamp >= ? AND deleted = 0
            GROUP BY hour
            ORDER BY count DESC
            LIMIT 1
        """
        top_hour = await self.stats_repo.fetch_one(top_hour_query, (guild_id, cutoff_str))
        
        # Среднее сообщений в день
        avg_per_day_query = """
            SELECT COUNT(*) * 1.0 / ? as avg_per_day
            FROM messages
            WHERE guild_id = ? AND timestamp >= ? AND deleted = 0
        """
        avg_per_day = await self.stats_repo.fetch_one(avg_per_day_query, (period, guild_id, cutoff_str))
        
        # Сообщения по дням недели
        daily_query = """
            SELECT 
                CASE cast(strftime('%w', timestamp) as integer)
                    WHEN 0 THEN 'Вс'
                    WHEN 1 THEN 'Пн'
                    WHEN 2 THEN 'Вт'
                    WHEN 3 THEN 'Ср'
                    WHEN 4 THEN 'Чт'
                    WHEN 5 THEN 'Пт'
                    WHEN 6 THEN 'Сб'
                END as day,
                COUNT(*) as count
            FROM messages
            WHERE guild_id = ? AND timestamp >= ? AND deleted = 0
            GROUP BY day
            ORDER BY strftime('%w', timestamp)
        """
        daily_stats = await self.stats_repo.fetch_all(daily_query, (guild_id, cutoff_str))
        
        # Голосовая статистика
        voice_query = """
            SELECT 
                COUNT(DISTINCT user_id) as voice_users,
                SUM(voice_minutes) as total_voice_minutes
            FROM user_stats
            WHERE guild_id = ? AND voice_minutes > 0
        """
        voice_stats = await self.stats_repo.fetch_one(voice_query, (guild_id,))
        
        # Топ-3 по голосу
        top_voice_query = """
            SELECT user_id, voice_minutes
            FROM user_stats
            WHERE guild_id = ? AND voice_minutes > 0
            ORDER BY voice_minutes DESC
            LIMIT 3
        """
        top_voice = await self.stats_repo.fetch_all(top_voice_query, (guild_id,))
        
        return {
            "total_messages": row["total_messages"] or 0,
            "active_users": row["active_users"] or 0,
            "active_channels": row["active_channels"] or 0,
            "avg_per_day": round(avg_per_day["avg_per_day"] or 0, 1),
            "top_user_id": top_user["user_id"] if top_user else None,
            "top_user_count": top_user["count"] if top_user else 0,
            "top_channel_id": top_channel["channel_id"] if top_channel else None,
            "top_channel_count": top_channel["count"] if top_channel else 0,
            "top_hour": top_hour["hour"] if top_hour else None,
            "top_hour_count": top_hour["count"] if top_hour else 0,
            "daily_stats": daily_stats,
            "voice_users": voice_stats["voice_users"] or 0,
            "total_voice_minutes": voice_stats["total_voice_minutes"] or 0,
            "top_voice": top_voice,
        }