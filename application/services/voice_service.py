from __future__ import annotations

import asyncio
import random
from datetime import datetime, timezone, timedelta
from typing import Dict, Optional
import disnake

from infrastructure.database.repositories.voice_repository import VoiceRepository
from infrastructure.logging import get_logger

logger = get_logger(__name__)

MSK = timezone(timedelta(hours=3))


class VoiceService:
    """Сервис для управления временными голосовыми комнатами"""

    def __init__(self, repo: VoiceRepository):
        self.repo = repo
        self._delete_tasks: Dict[int, asyncio.Task] = {}
        self._creating: set = set()

    async def create(self, member: disnake.Member, trigger_channel: disnake.VoiceChannel) -> Optional[disnake.VoiceChannel]:
        key = (member.id, member.guild.id)
        if key in self._creating:
            return None

        existing = await self.repo.get_by_owner(member.id, member.guild.id)
        if existing:
            ch = member.guild.get_channel(existing["channel_id"])
            if ch:
                try:
                    await member.move_to(ch)
                except:
                    pass
                return None
            else:
                await self.repo.delete(existing["channel_id"])

        self._creating.add(key)
        try:
            guild = member.guild
            category = trigger_channel.category
            name = f"🔊 {member.display_name}"

            channel = await guild.create_voice_channel(
                name=name,
                category=category,
                overwrites={
                    guild.default_role: disnake.PermissionOverwrite(connect=False),
                    member: disnake.PermissionOverwrite(connect=True, manage_channels=True, manage_permissions=True, move_members=True)
                }
            )
            await member.move_to(channel)
            await self.repo.create(channel.id, guild.id, member.id, name)
            logger.info(f"Voice room created: {channel.name}")
            return channel
        except Exception as e:
            logger.error(f"Failed to create voice room: {e}")
            return None
        finally:
            self._creating.discard(key)

    async def delete(self, channel: disnake.VoiceChannel):
        try:
            await self.repo.delete(channel.id)
            await channel.delete()
            logger.info(f"Voice room deleted: {channel.name}")
        except Exception as e:
            logger.error(f"Failed to delete voice room: {e}")

    async def schedule_delete(self, channel: disnake.VoiceChannel, delay: float = 30.0):
        if channel.id in self._delete_tasks:
            self._delete_tasks[channel.id].cancel()

        async def delayed():
            await asyncio.sleep(delay)
            if len(channel.members) == 0:
                await self.delete(channel)
            self._delete_tasks.pop(channel.id, None)

        self._delete_tasks[channel.id] = asyncio.create_task(delayed())

    async def cancel_delete(self, channel_id: int):
        if channel_id in self._delete_tasks:
            self._delete_tasks[channel_id].cancel()
            del self._delete_tasks[channel_id]

    async def handle_owner_leave(self, channel: disnake.VoiceChannel, old_owner: disnake.Member):
        from presentation.cogs.voice_cog import VoiceControlView

        members = [m for m in channel.members if not m.bot and m.id != old_owner.id]
        if not members:
            return

        new_owner = random.choice(members)

        try:
            await channel.set_permissions(old_owner, overwrite=None)
            await channel.set_permissions(new_owner, connect=True, manage_channels=True, manage_permissions=True, move_members=True)
            await self.repo.update_owner(channel.id, new_owner.id)
            await channel.edit(name=f"🔊 {new_owner.display_name}")

            view = VoiceControlView(self)
            async for msg in channel.history(limit=10):
                if msg.author == channel.guild.me and msg.embeds:
                    embed = msg.embeds[0]
                    embed.set_field_at(0, name="👑 Владелец", value=new_owner.mention, inline=True)
                    await msg.edit(embed=embed, view=view)
                    break

            logger.info(f"Ownership auto-transferred to {new_owner.display_name}")
        except Exception as e:
            logger.error(f"Failed to auto-transfer: {e}")

    async def rename(self, channel: disnake.VoiceChannel, new_name: str, user: disnake.Member) -> bool:
        if not channel.permissions_for(user).manage_channels:
            return False
        try:
            await channel.edit(name=new_name)
            return True
        except:
            return False

    async def limit(self, channel: disnake.VoiceChannel, limit: int, user: disnake.Member) -> bool:
        if not channel.permissions_for(user).manage_channels:
            return False
        try:
            await channel.edit(user_limit=limit)
            return True
        except:
            return False

    async def lock(self, channel: disnake.VoiceChannel, user: disnake.Member) -> bool:
        if not channel.permissions_for(user).manage_permissions:
            return False
        try:
            await channel.set_permissions(user.guild.default_role, connect=False)
            return True
        except:
            return False

    async def unlock(self, channel: disnake.VoiceChannel, user: disnake.Member) -> bool:
        if not channel.permissions_for(user).manage_permissions:
            return False
        try:
            await channel.set_permissions(user.guild.default_role, connect=True)
            return True
        except:
            return False

    async def transfer(self, channel: disnake.VoiceChannel, new_owner: disnake.Member, user: disnake.Member) -> bool:
        if not channel.permissions_for(user).manage_permissions:
            return False
        try:
            await channel.set_permissions(user, overwrite=None)
            await channel.set_permissions(new_owner, connect=True, manage_channels=True, manage_permissions=True, move_members=True)
            await self.repo.update_owner(channel.id, new_owner.id)
            await channel.edit(name=f"🔊 {new_owner.display_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to transfer: {e}")
            return False

    async def invite(self, channel: disnake.VoiceChannel, target: disnake.Member, user: disnake.Member) -> bool:
        if not channel.permissions_for(user).manage_permissions:
            return False
        try:
            await channel.set_permissions(target, connect=True)
            await channel.send(f"📩 {target.mention}, вас пригласил {user.mention}!")
            try:
                await target.send(f"📩 **{user.display_name}** приглашает вас в **{channel.name}**!\n{channel.mention}")
            except:
                pass
            return True
        except:
            return False

    async def kick(self, channel: disnake.VoiceChannel, target: disnake.Member, user: disnake.Member) -> bool:
        if not channel.permissions_for(user).manage_permissions:
            return False
        try:
            await channel.set_permissions(target, connect=False)
            if target.voice and target.voice.channel == channel:
                await target.move_to(None)
            return True
        except:
            return False
        
    async def ban(self, channel: disnake.VoiceChannel, target: disnake.Member, user: disnake.Member) -> bool:
        if not channel.permissions_for(user).manage_permissions:
            return False
        try:
            await channel.set_permissions(target, connect=False)
            if target.voice and target.voice.channel == channel:
                await target.move_to(None)
            return True
        except:
            return False