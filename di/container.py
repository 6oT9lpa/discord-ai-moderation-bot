from typing import Optional

from infrastructure.config import get_config, BotConfig
from infrastructure.database.connection import DatabaseManager
from infrastructure.database.repositories.role_repository import RoleRepository
from infrastructure.database.repositories.punishment_repository import PunishmentRepository
from application.services.role_service import RoleService
from application.services.admin_service import AdminService
from application.services.ai_service import AIService
from infrastructure.ai.ollama_client import OllamaClient
from infrastructure.logging import get_logger

logger = get_logger(__name__)


class Container:
    def __init__(self):
        self.config: BotConfig = get_config()
        
        self._database: Optional[DatabaseManager] = None
        self._role_repo: Optional[RoleRepository] = None
        self._role_service: Optional[RoleService] = None
        self._punishment_repo: Optional[PunishmentRepository] = None
        self._admin_service: Optional[AdminService] = None
        self._ollama_client: Optional[OllamaClient] = None
        self._ai_service: Optional[AIService] = None

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
    
    async def get_punishment_repository(self) -> PunishmentRepository:
        """Получить репозиторий наказаний"""
        if not self._punishment_repo:
            db = await self.get_database()
            self._punishment_repo = PunishmentRepository(db)
        return self._punishment_repo
    
    async def get_role_service(self) -> RoleService:
        """Получить сервис ролей"""
        if not self._role_service:
            repo = await self.get_role_repository()
            self._role_service = RoleService(repo, self.config)
        return self._role_service
    
    async def get_admin_service(self) -> AdminService:
        """Получить сервис администрирования"""
        if not self._admin_service:
            repo = await self.get_punishment_repository()
            self._admin_service = AdminService(repo)
        return self._admin_service
    
    async def get_ollama_client(self) -> OllamaClient:
        """Получить клиент Ollama"""
        if not self._ollama_client:
            self._ollama_client = OllamaClient(
                base_url=self.config.ollama_base_url,
                model=self.config.ollama_model
            )
        return self._ollama_client
    
    async def get_ai_service(self) -> AIService:
        """Получить сервис ИИ"""
        if not self._ai_service:
            ollama = await self.get_ollama_client()
            self._ai_service = AIService(ollama)
        return self._ai_service
    
    async def shutdown(self):
        """Закрытие ресурсов"""
        if self._database:
            await self._database.close()
        if self._ollama_client:
            await self._ollama_client.close_session()
