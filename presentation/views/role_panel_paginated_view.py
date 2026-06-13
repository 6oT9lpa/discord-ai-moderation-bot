import disnake
from disnake.ui import Button

from presentation.views.base import BaseView
from presentation.views.role_button import RoleButton
from infrastructure.logging.logger import get_logger

logger = get_logger(__name__)


class RolePanelPaginatedView(BaseView):
    def __init__(self, roles: list, items_per_page: int = 10):
        super().__init__(timeout=None)
        self._roles = roles
        self._items_per_page = items_per_page
        self._current_page = 0
        self._total_pages = (len(roles) + items_per_page - 1) // items_per_page
        
        logger.info(f"Creating RolePanelPaginatedView with {len(roles)} roles, {self._total_pages} pages")
        
        self._update_buttons()
    
    def _update_buttons(self):
        """Обновить кнопки на текущей странице"""
        self.clear_items()
        
        start = self._current_page * self._items_per_page
        end = min(start + self._items_per_page, len(self._roles))
        page_roles = self._roles[start:end]
        
        logger.debug(f"Page {self._current_page + 1}: showing {len(page_roles)} roles")
        
        for role in page_roles:
            button = RoleButton(
                role_id=role['role_id'],
                role_name=role['name'],
                emoji=role.get('display_emoji')
            )
            self.add_item(button)
        
        if self._total_pages > 1:
            self._add_navigation_buttons()
    
    def _add_navigation_buttons(self):
        """Добавить кнопки навигации"""
        if self._current_page > 0:
            prev_button = Button(
                label="◀ Назад",
                style=disnake.ButtonStyle.secondary,
                custom_id="prev_page"
            )
            prev_button.callback = self._previous_page
            self.add_item(prev_button)
            logger.debug("Added previous page button")
        
        page_indicator = Button(
            label=f"{self._current_page + 1}/{self._total_pages}",
            style=disnake.ButtonStyle.secondary,
            disabled=True,
            custom_id="page_indicator"
        )
        self.add_item(page_indicator)
        
        if self._current_page < self._total_pages - 1:
            next_button = Button(
                label="Вперёд ▶",
                style=disnake.ButtonStyle.secondary,
                custom_id="next_page"
            )
            next_button.callback = self._next_page
            self.add_item(next_button)
            logger.debug("Added next page button")
    
    async def _previous_page(self, interaction: disnake.MessageInteraction):
        """Переход на предыдущую страницу"""
        logger.info(f"User {interaction.user} navigated to previous page (current: {self._current_page + 1})")
        self._current_page -= 1
        self._update_buttons()
        await interaction.response.edit_message(view=self)
    
    async def _next_page(self, interaction: disnake.MessageInteraction):
        """Переход на следующую страницу"""
        logger.info(f"User {interaction.user} navigated to next page (current: {self._current_page + 1})")
        self._current_page += 1
        self._update_buttons()
        await interaction.response.edit_message(view=self)