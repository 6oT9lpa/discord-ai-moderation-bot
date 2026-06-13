import disnake
from disnake.ui import Button

from presentation.views.base import BaseView
from infrastructure.logging.logger import get_logger

logger = get_logger(__name__)


class CloseButtonView(BaseView):  
    def __init__(self, timeout: float = 60.0):
        super().__init__(timeout=timeout)
        logger.debug(f"CloseButtonView created with timeout {timeout}s")
    
    @disnake.ui.button(label="Закрыть", style=disnake.ButtonStyle.secondary, emoji="🔒")
    async def close(self, button: Button, interaction: disnake.MessageInteraction):
        logger.info(f"User {interaction.user} closed the panel")
        await interaction.response.edit_message(content="Панель закрыта", view=None)
    
    async def on_timeout(self):
        """Обработка таймаута"""
        logger.info("CloseButtonView timed out")
        await super().on_timeout()