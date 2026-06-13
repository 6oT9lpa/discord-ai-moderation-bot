import disnake
from disnake.ui import Button

from infrastructure.logging.logger import get_logger

logger = get_logger(__name__)


class RoleButton(Button):
    def __init__(self, role_id: int, role_name: str, emoji: str = None):
        label = role_name
        if emoji:
            label = f"{emoji} {role_name}"
        
        super().__init__(
            label=label,
            style=disnake.ButtonStyle.primary,
            custom_id=f"role_{role_id}"
        )
        self.role_id = role_id
        logger.debug(f"RoleButton created: {label} (ID: {role_id})")
    
    async def callback(self, interaction: disnake.MessageInteraction):
        """Обработка нажатия на кнопку"""
        user = interaction.user
        logger.info(f"RoleButton clicked: {self.label} by {user} (ID: {user.id})")
        
        role = interaction.guild.get_role(self.role_id)
        if not role:
            logger.warning(f"Role {self.role_id} not found in guild {interaction.guild.id}")
            await interaction.response.send_message("Роль не найдена", ephemeral=True)
            return
        
        member = interaction.user
        
        if role in member.roles:
            logger.info(f"Removing role {role.name} from {member}")
            await member.remove_roles(role, reason="Снятие через панель ролей")
            await interaction.response.send_message(f"Роль **{role.name}** снята", ephemeral=True)
            logger.info(f"Role {role.name} removed from {member}")

        else:
            if interaction.guild.me.top_role.position <= role.position:
                logger.warning(f"Cannot assign role {role.name} - bot role is lower")
                await interaction.response.send_message("Не могу выдать эту роль (она выше моей)", ephemeral=True)
                return
            
            logger.info(f"Assigning role {role.name} to {member}")
            await member.add_roles(role, reason="Выдача через панель ролей")
            await interaction.response.send_message(f"Роль **{role.name}** выдана", ephemeral=True)
            logger.info(f"Role {role.name} assigned to {member}")