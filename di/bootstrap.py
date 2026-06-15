import asyncio
import signal
import sys
import disnake
from disnake.ext import commands

from di import Container
from presentation import DiscordBot
from infrastructure.logging import get_logger 
from presentation.cogs.admin_cog import AdminCog
from presentation.cogs.roles_cog import RolesCog
from presentation.cogs.ai_cog import AICog

logger = get_logger(__name__)


class Bootstrap:
    def __init__(self):
        self.container = Container()
        self.bot: DiscordBot = None
        self._admin_service = None
        self._role_service = None
        self._ai_service = None

    async def run(self):
        """Запуск бота"""
        try:
            self._role_service = await self.container.get_role_service()
            self._admin_service = await self.container.get_admin_service()
            self._ai_service = await self.container.get_ai_service()
            self._db = await self.container.get_database()

            if self._role_service is None:
                logger.error("Failed to get role service from container!")
                return
            
            if self._admin_service is None:
                logger.error("Failed to get admin service from container!")
                return
            
            if self._ai_service is None:
                logger.error("Failed to get AI service from container!")
                return
            
            logger.info(f"Role service obtained: {self._role_service}")
            logger.info(f"Admin service obtained: {self._admin_service}")
            logger.info(f"AI service obtained: {self._ai_service}")
            
            # Создаём бота
            self.bot = DiscordBot(
                config=self.container.config,
                role_service=self._role_service
            )
            
            # Регистрируем команды
            await self._register_commands()
            
            # Настраиваем обработку сигналов
            self._setup_signal_handlers()
            
            # Запускаем
            token = self.container.config.discord_token.get_secret_value()
            logger.info("Starting bot...")
            await self.bot.start(token)
            
        except KeyboardInterrupt:
            logger.info("KeyboardInterrupt received. Shutting down...")
            await self._shutdown()
        except asyncio.CancelledError:
            logger.info("Task cancelled. Shutting down...")
            await self._shutdown()
        except Exception as e:
            logger.error(f"Unexpected error: {e}", exc_info=True)
            await self._shutdown()
            sys.exit(1)
    
    def _setup_signal_handlers(self):
        """Настройка обработки сигналов для graceful shutdown"""
        try:
            loop = asyncio.get_event_loop()
            
            for sig in (signal.SIGTERM, signal.SIGINT):
                try:
                    loop.add_signal_handler(
                        sig,
                        lambda s=sig: asyncio.create_task(self._shutdown())
                    )
                except (NotImplementedError, ValueError):
                    pass
        except Exception as e:
            logger.warning(f"Could not setup signal handlers: {e}")
    
    async def _register_commands(self):
        """Регистрация команд"""
        logger.info("Registering commands...")
        
        self.bot.add_cog(RolesCog(self.bot, self._role_service))
        logger.info("  ✅ RolesCog registered")
        self.bot.add_cog(AdminCog(self.bot, self._role_service, self._admin_service))
        logger.info("  ✅ AdminCog registered")
        self.bot.add_cog(AICog(self.bot, self._ai_service, self._admin_service, self._db))
        logger.info("  ✅ AICog registered")

        logger.info("All cogs registered successfully")
        
        
    async def _shutdown(self):
        logger.info("Shutting down...")
        
        # Закрываем бота
        if self.bot and not self.bot.is_closed():
            try:
                await self.bot.close()
                logger.info("Bot closed")
            except Exception as e:
                logger.error(f"Error closing bot: {e}")
        
        # Закрываем контейнер
        if self.container:
            try:
                await self.container.shutdown()
                logger.info("Container shutdown complete")
            except Exception as e:
                logger.error(f"Error shutting down container: {e}")
        
        logger.info("Shutdown complete")

def handle_exception(loop, context):
    """Обработка необработанных исключений"""
    msg = context.get("exception", context["message"])
    logger.error(f"Unhandled exception: {msg}")
    loop.stop()