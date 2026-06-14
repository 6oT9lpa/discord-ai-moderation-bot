from typing import Optional

from infrastructure.config import get_config, BotConfig
from infrastructure.database import DatabaseManager
from infrastructure.database import (
    RoleRepository,
    WelcomeConfigRepository,
    ChannelConfigRepository,
    RolePanelMessageRepository,
    RolePanelButtonRepository,
)
from application.services import RoleService, WelcomeService, ChannelService
from infrastructure.logging import get_logger
from di.modules import MemberEventsModule

logger = get_logger(__name__)


class Container:
    def __init__(self):
        self.config: BotConfig = get_config()
        
        self._database: Optional[DatabaseManager] = None
        self._role_repo: Optional[RoleRepository] = None
        self._role_service: Optional[RoleService] = None
        self._panel_message_repo: Optional[RolePanelMessageRepository] = None
        self._panel_button_repo: Optional[RolePanelButtonRepository] = None
        self._channel_config_repo: Optional[ChannelConfigRepository] = None
        self._channel_service: Optional[ChannelService] = None
        self._welcome_config_repo: Optional[WelcomeConfigRepository] = None
        self._welcome_service: Optional[WelcomeService] = None
        self._member_events_module: Optional[MemberEventsModule] = None

        logger.info("DI Container initialized")

    async def get_database(self) -> DatabaseManager:
        if not self._database:
            self._database = DatabaseManager(self.config.database_url)
            await self._database.connect()
            await self._database.initialize()
        return self._database
    
    #=============== Repository =====================
    async def get_role_repository(self) -> RoleRepository:
        if not self._role_repo:
            db = await self.get_database()
            self._role_repo = RoleRepository(db, self.config.discord_guild_id)
        return self._role_repo
    
    async def get_panel_message_repository(self) -> RolePanelMessageRepository:
        if not self._panel_message_repo:
            db = await self.get_database()
            self._panel_message_repo = RolePanelMessageRepository(db)
        return self._panel_message_repo
    
    async def get_panel_button_repository(self) -> RolePanelButtonRepository:
        if not self._panel_button_repo:
            db = await self.get_database()
            self._panel_button_repo = RolePanelButtonRepository(db)
        return self._panel_button_repo
    
    async def get_channel_config_repository(self) -> ChannelConfigRepository:
        if not self._channel_config_repo:
            db = await self.get_database()
            self._channel_config_repo = ChannelConfigRepository(db)
        return self._channel_config_repo
    
    async def get_welcome_config_repository(self) -> WelcomeConfigRepository:
        if not self._welcome_config_repo:
            db = await self.get_database()
            self._welcome_config_repo = WelcomeConfigRepository(db)
        return self._welcome_config_repo

    #=============== Service =====================

    async def get_role_service(self) -> RoleService:
        if not self._role_service:
            repo = await self.get_role_repository()
            self._role_service = RoleService(repo, self.config)
            
            panel_message_repo = await self.get_panel_message_repository()
            panel_button_repo = await self.get_panel_button_repository()
            self._role_service.set_panel_repositories(panel_message_repo, panel_button_repo)
            
            logger.info("RoleService created with panel repositories")
            
        return self._role_service
    
    async def get_welcome_service(self) -> WelcomeService:
        if not self._welcome_service:
            repo = await self.get_welcome_config_repository()
            self._welcome_service = WelcomeService(repo)
            logger.info("WelcomeService created")
        return self._welcome_service
    
    async def get_channel_service(self) -> ChannelService:
        if not self._channel_service:
            repo = await self.get_channel_config_repository()
            self._channel_service = ChannelService(repo)
            logger.info("ChannelService created")
        return self._channel_service
    
    def get_member_events_module(self) -> MemberEventsModule:
        if not self._member_events_module:
            self._member_events_module = MemberEventsModule(self)
        return self._member_events_module
    
    async def shutdown(self):
        if self._database:
            await self._database.close()
        
        if self._member_events_module:
            await self._member_events_module.shutdown()
        
        logger.info("Container shutdown complete")