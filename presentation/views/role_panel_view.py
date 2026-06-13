from presentation.views.base import BaseView
from presentation.views.role_button import RoleButton
from infrastructure.logging.logger import get_logger

logger = get_logger(__name__)


class RolePanelView(BaseView):
    def __init__(self, roles: list):
        super().__init__(timeout=None)
        
        logger.info(f"Creating RolePanelView with {len(roles)} roles")
        
        for role in roles:
            button = RoleButton(
                role_id=role['role_id'],
                role_name=role['name'],
                emoji=role.get('display_emoji')
            )
            self.add_item(button)
        
        logger.debug(f"RolePanelView created with {len(self.children)} buttons")