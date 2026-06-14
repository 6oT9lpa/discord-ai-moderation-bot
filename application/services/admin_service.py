from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta

from infrastructure.database.repositories.punishment_repository import PunishmentRepository
from infrastructure.logging import get_logger

logger = get_logger(__name__)


class AdminService:
    """
    Сервис для управления наказаниями и администрированием
    """
    
    def __init__(self, punishment_repo: PunishmentRepository):
        self._punishment_repo = punishment_repo
        logger.info("AdminService initialized")

    async def log_warning(
        self,
        user_id: int,
        mod_id: int,
        reason: Optional[str] = None
    ) -> int:
        """
        Зарегистрировать предупреждение
        
        Args:
            user_id: ID пользователя
            mod_id: ID модератора
            reason: Причина предупреждения
            
        Returns:
            ID созданного наказания
        """
        punishment_id = await self._punishment_repo.create_punishment(
            user_id=user_id,
            mod_id=mod_id,
            punishment_type="warn",
            reason=reason
        )
        logger.info(f"Warning logged for user {user_id} by moderator {mod_id}")
        return punishment_id

    async def log_mute(
        self,
        user_id: int,
        mod_id: int,
        hours: int = 0,
        minutes: int = 0,
        reason: Optional[str] = None
    ) -> int:
        """
        Зарегистрировать мьют
        
        Args:
            user_id: ID пользователя
            mod_id: ID модератора
            hours: Часы мьюта
            minutes: Минуты мьюта
            reason: Причина мьюта
            
        Returns:
            ID созданного наказания
        """
        duration_str = self._format_duration(hours, minutes)
        expires_at = datetime.now() + timedelta(hours=hours, minutes=minutes)
        
        punishment_id = await self._punishment_repo.create_punishment(
            user_id=user_id,
            mod_id=mod_id,
            punishment_type="mute",
            reason=reason,
            duration=duration_str,
            expires_at=expires_at
        )
        logger.info(f"Mute logged for user {user_id} by moderator {mod_id} for {duration_str}")
        return punishment_id

    async def log_kick(
        self,
        user_id: int,
        mod_id: int,
        reason: Optional[str] = None
    ) -> int:
        """
        Зарегистрировать кик
        
        Args:
            user_id: ID пользователя
            mod_id: ID модератора
            reason: Причина кика
            
        Returns:
            ID созданного наказания
        """
        punishment_id = await self._punishment_repo.create_punishment(
            user_id=user_id,
            mod_id=mod_id,
            punishment_type="kick",
            reason=reason
        )
        logger.info(f"Kick logged for user {user_id} by moderator {mod_id}")
        return punishment_id

    async def log_ban(
        self,
        user_id: int,
        mod_id: int,
        reason: Optional[str] = None,
        duration: Optional[str] = None
    ) -> int:
        """
        Зарегистрировать бан
        
        Args:
            user_id: ID пользователя
            mod_id: ID модератора
            reason: Причина бана
            duration: Длительность бана (если временный)
            
        Returns:
            ID созданного наказания
        """
        punishment_id = await self._punishment_repo.create_punishment(
            user_id=user_id,
            mod_id=mod_id,
            punishment_type="ban",
            reason=reason,
            duration=duration
        )
        logger.info(f"Ban logged for user {user_id} by moderator {mod_id}")
        return punishment_id

    async def log_unmute(
        self,
        user_id: int,
        mod_id: int,
        reason: Optional[str] = None
    ) -> None:
        """
        Зарегистрировать размут (деактивировать мьют)
        
        Args:
            user_id: ID пользователя
            mod_id: ID модератора
            reason: Причина размута
        """
        # Найти активный мьют
        violations = await self._punishment_repo.get_violations_by_type(user_id, "mute")
        if violations:
            for violation in violations:
                if violation["active"]:
                    await self._punishment_repo.deactivate_punishment(violation["id"])
                    logger.info(f"Unmute logged for user {user_id} by moderator {mod_id}")
                    return
        
        logger.warning(f"No active mute found for user {user_id}")

    async def log_unban(
        self,
        user_id: int,
        mod_id: int,
        reason: Optional[str] = None
    ) -> None:
        """
        Зарегистрировать разбан (деактивировать бан)
        
        Args:
            user_id: ID пользователя
            mod_id: ID модератора
            reason: Причина разбана
        """
        # Найти активный бан
        violations = await self._punishment_repo.get_violations_by_type(user_id, "ban")
        if violations:
            for violation in violations:
                if violation["active"]:
                    await self._punishment_repo.deactivate_punishment(violation["id"])
                    logger.info(f"Unban logged for user {user_id} by moderator {mod_id}")
                    return
        
        logger.warning(f"No active ban found for user {user_id}")

    async def get_user_violations(self, user_id: int) -> List[Dict[str, Any]]:
        """
        Получить все нарушения пользователя
        
        Args:
            user_id: ID пользователя
            
        Returns:
            Список нарушений
        """
        return await self._punishment_repo.get_user_violations(user_id)

    async def get_violation_count(self, user_id: int, active_only: bool = False) -> int:
        """
        Получить количество нарушений пользователя
        
        Args:
            user_id: ID пользователя
            active_only: Только активные наказания
            
        Returns:
            Количество нарушений
        """
        return await self._punishment_repo.get_violation_count(user_id, active_only)

    async def get_violations_summary(self, user_id: int) -> Dict[str, Any]:
        """
        Получить сводку нарушений пользователя
        
        Args:
            user_id: ID пользователя
            
        Returns:
            Словарь с информацией о нарушениях
        """
        total = await self._punishment_repo.get_violation_count(user_id, active_only=False)
        active = await self._punishment_repo.get_violation_count(user_id, active_only=True)
        by_type = await self._punishment_repo.count_active_punishments_by_type(user_id)
        
        return {
            "total": total,
            "active": active,
            "by_type": by_type
        }

    @staticmethod
    def _format_duration(hours: int, minutes: int) -> str:
        """
        Форматировать длительность
        
        Args:
            hours: Часы
            minutes: Минуты
            
        Returns:
            Отформатированная строка
        """
        parts = []
        if hours > 0:
            parts.append(f"{hours}h")
        if minutes > 0:
            parts.append(f"{minutes}m")
        
        return " ".join(parts) if parts else "0m"
