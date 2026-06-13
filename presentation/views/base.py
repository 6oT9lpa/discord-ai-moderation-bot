from disnake.ui import View

from infrastructure.logging import get_logger

logger = get_logger(__name__)


class BaseView(View):
    def __init__(self, timeout: float = None):
        super().__init__(timeout=timeout)
        logger.debug(f"View {self.__class__.__name__} created with timeout={timeout}")
    
    async def disable_all_items(self):
        """Отключить все кнопки во View"""
        for item in self.children:
            item.disabled = True

        logger.debug(f"All items disabled in {self.__class__.__name__}")
    
    async def on_timeout(self):
        """Обработка таймаута"""
        logger.info(f"View {self.__class__.__name__} timed out")
        await self.disable_all_items()