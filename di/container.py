from typing import Optional

from infrastructure.config import get_config, BotConfig
from infrastructure.database.connection import DatabaseManager
from infrastructure.database.repositories.role_repository import RoleRepository
from application.services.role_service import RoleService
from application.services.stats_service import StatsService
from infrastructure.database.repositories.stats_repository import StatsRepository
from application.services.voice_service import VoiceService
from infrastructure.database.repositories.voice_repository import VoiceRepository
from infrastructure.logging import get_logger

logger = get_logger(__name__)


class Container:
    def __init__(self):
        self.config: BotConfig = get_config()
        
        self._database: Optional[DatabaseManager] = None
        self._role_repo: Optional[RoleRepository] = None
        self._role_service: Optional[RoleService] = None
        self._stats_service: Optional[StatsService] = None
        self._stats_repo: Optional[StatsRepository] = None
        self._voice_service: Optional[VoiceService] = None
        self._voice_repo: Optional[VoiceRepository] = None

        logger.info("DI Container initialized")

    async def get_database(self) -> DatabaseManager:
        """Получить менеджер БД"""
        if not self._database:
            self._database = DatabaseManager(self.config.database_url)
            await self._database.connect()
            await self._database.initialize()
        return self._database
    
    async def get_role_repository(self) -> RoleRepository:
        """Получить репозиторий ролей"""
        if not self._role_repo:
            db = await self.get_database()
            self._role_repo = RoleRepository(db, self.config.discord_guild_id)
        return self._role_repo
    
    async def get_role_service(self) -> RoleService:
        """Получить сервис ролей"""
        if not self._role_service:
            repo = await self.get_role_repository()
            self._role_service = RoleService(repo, self.config)
        return self._role_service
    
    async def get_stats_service(self) -> StatsService:
        """Получить сервис статистики"""
        if not self._stats_service:
            repo = await self.get_stats_repository()
            self._stats_service = StatsService(repo, self.config)  
        return self._stats_service
    
    async def get_stats_repository(self) -> StatsRepository:
        """Получить репозиторий статистики"""
        if not self._stats_repo:
            db = await self.get_database()
            self._stats_repo = StatsRepository(db)  
        return self._stats_repo
    
    async def get_voice_service(self) -> VoiceService:
        """Получить сервис войсов"""
        if not self._voice_service:
            repo = await self.get_voice_repository()
            self._voice_service = VoiceService(repo)  
        return self._voice_service
    
    async def get_voice_repository(self) -> VoiceRepository:
        """Получить репозиторий войсов"""
        if not self._voice_repo:
            db = await self.get_database()
            self._voice_repo = VoiceRepository(db)  
        return self._voice_repo

    async def shutdown(self):
        """Закрытие ресурсов"""
        if self._database:
            await self._database.close()