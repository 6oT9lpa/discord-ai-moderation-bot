import disnake
from disnake.ui import Button

from presentation.views.base import BaseView
from infrastructure.logging.logger import get_logger

logger = get_logger(__name__)


class ConfirmView(BaseView):
    def __init__(self, timeout: float = 60.0):
        super().__init__(timeout=timeout)
        self.value = None
        logger.debug(f"ConfirmView created with timeout {timeout}s")
    
    @disnake.ui.button(label="Подтвердить", style=disnake.ButtonStyle.green)
    async def confirm(self, button: Button, interaction: disnake.MessageInteraction):
        logger.info(f"User {interaction.user} confirmed action")
        self.value = True
        self.stop()
        await interaction.response.edit_message(content="Действие подтверждено", view=None)
    
    @disnake.ui.button(label="Отмена", style=disnake.ButtonStyle.red)
    async def cancel(self, button: Button, interaction: disnake.MessageInteraction):
        logger.info(f"User {interaction.user} cancelled action")
        self.value = False
        self.stop()
        await interaction.response.edit_message(content="Действие отменено", view=None)
    
    async def on_timeout(self):
        """Обработка таймаута"""
        logger.info("ConfirmView timed out")
        self.value = False
        await super().on_timeout()