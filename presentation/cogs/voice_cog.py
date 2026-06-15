from __future__ import annotations

import disnake
from disnake.ext import commands
from typing import Optional, List

from application.services.voice_service import VoiceService
from infrastructure.logging import get_logger

logger = get_logger(__name__)


class VoiceControlView(disnake.ui.View):
    def __init__(self, service: VoiceService):
        super().__init__(timeout=None)
        self.service = service

    @disnake.ui.string_select(
        placeholder="🎛️ Выберите действие...",
        custom_id="voice_actions",
        options=[
            disnake.SelectOption(label="✏️ Переименовать", value="rename", emoji="✏️"),
            disnake.SelectOption(label="👥 Лимит", value="limit", emoji="👥"),
            disnake.SelectOption(label="🔒 Закрыть", value="lock", emoji="🔒"),
            disnake.SelectOption(label="🔓 Открыть", value="unlock", emoji="🔓"),
            disnake.SelectOption(label="📩 Пригласить", value="invite", emoji="📩"),
            disnake.SelectOption(label="👢 Выгнать", value="kick", emoji="👢"),
            disnake.SelectOption(label="🔄 Передать", value="transfer", emoji="🔄"),
            disnake.SelectOption(label="🌍 Регион", value="region", emoji="🌍"),
            disnake.SelectOption(label="🗑️ Удалить", value="delete", emoji="🗑️"),
            disnake.SelectOption(label="🔨 Забанить", value="ban", emoji="🔨"),
        ]
    )
    async def voice_actions(self, select: disnake.ui.StringSelect, inter: disnake.MessageInteraction):
        vc = inter.author.voice.channel if inter.author.voice else None
        if not vc:
            return await inter.response.send_message("❌ Вы не в голосовом канале!", ephemeral=True)

        action = select.values[0]

        if action == "rename":
            await inter.response.send_modal(VoiceRenameModal(self.service))
        elif action == "limit":
            await inter.response.send_modal(VoiceLimitModal(self.service))
        elif action == "lock":
            ok = await self.service.lock(vc, inter.author)
            await inter.response.send_message("🔒 Закрыто!" if ok else "❌ Нет прав!", ephemeral=True)
        elif action == "unlock":
            ok = await self.service.unlock(vc, inter.author)
            await inter.response.send_message("🔓 Открыто!" if ok else "❌ Нет прав!", ephemeral=True)
        elif action == "invite":
            await inter.response.send_modal(VoiceInviteModal(self.service))
        elif action == "kick":
            members = [m for m in vc.members if not m.bot and m.id != inter.author.id]
            if not members:
                return await inter.response.send_message("❌ Некого!", ephemeral=True)
            view = MemberSelectView(self.service, vc, "kick", members)
            await inter.response.send_message("👢 Выберите:", view=view, ephemeral=True)
        elif action == "transfer":
            members = [m for m in vc.members if not m.bot and m.id != inter.author.id]
            if not members:
                return await inter.response.send_message("❌ Некому!", ephemeral=True)
            view = MemberSelectView(self.service, vc, "transfer", members)
            await inter.response.send_message("🔄 Выберите:", view=view, ephemeral=True)
        elif action == "region":
            view = RegionSelectView(vc)
            await inter.response.send_message("🌍 Выберите:", view=view, ephemeral=True)
        elif action == "delete":
            if not vc.permissions_for(inter.author).manage_channels:
                return await inter.response.send_message("❌ Нет прав!", ephemeral=True)
            await self.service.delete(vc)
            await inter.response.send_message("🗑️ Удалено!", ephemeral=True)
        elif action == "ban":
            members = [m for m in vc.members if not m.bot and m.id != inter.author.id]
            if not members:
                return await inter.response.send_message("❌ Некого!", ephemeral=True)
            view = MemberSelectView(self.service, vc, "ban", members)
            await inter.response.send_message("🔨 Выберите кого забанить:", view=view, ephemeral=True)


class MemberSelectView(disnake.ui.View):
    def __init__(self, service: VoiceService, channel: disnake.VoiceChannel, action: str, members: List[disnake.Member]):
        super().__init__(timeout=60)
        self.service = service
        self.channel = channel
        self.action = action
        options = [disnake.SelectOption(label=m.display_name[:100], value=str(m.id), emoji="👤") for m in members[:25]]
        menu = disnake.ui.StringSelect(placeholder="Выберите...", custom_id="member_select", options=options)
        menu.callback = self.callback
        self.add_item(menu)

    async def callback(self, inter: disnake.MessageInteraction):
        target = inter.guild.get_member(int(inter.data["values"][0]))
        if not target:
            return await inter.response.send_message("❌ Не найден!", ephemeral=True)
        if self.action == "kick":
            ok = await self.service.kick(self.channel, target, inter.author)
            await inter.response.send_message("✅ Выгнан!" if ok else "❌ Нет прав!", ephemeral=True)
        elif self.action == "transfer":
            ok = await self.service.transfer(self.channel, target, inter.author)
            if ok:
                view = VoiceControlView(self.service)
                async for msg in self.channel.history(limit=5):
                    if msg.author == inter.guild.me and msg.embeds:
                        embed = msg.embeds[0]
                        embed.set_field_at(0, name="👑 Владелец", value=target.mention, inline=True)
                        await msg.edit(embed=embed, view=view)
                        break
                await inter.response.send_message("✅ Передано!", ephemeral=True)
            else:
                await inter.response.send_message("❌ Нет прав!", ephemeral=True)
        elif self.action == "ban":
            ok = await self.service.ban(self.channel, target, inter.author)
            await inter.response.send_message("🔨 Забанен!" if ok else "❌ Нет прав!", ephemeral=True)
        self.stop()


class RegionSelectView(disnake.ui.View):
    REGIONS = [
        ("🇧🇷 Бразилия", "brazil"), ("🇳🇱 Роттердам", "rotterdam"), ("🇮🇳 Индия", "india"),
        ("🇯🇵 Япония", "japan"), ("🇸🇬 Сингапур", "singapore"), ("🇿🇦 ЮАР", "southafrica"),
        ("🇦🇺 Сидней", "sydney"), ("🇪🇺 Европа", "europe"), ("🇺🇸 US East", "us-east"),
        ("🇺🇸 US West", "us-west"), ("🇺🇸 US Central", "us-central"), ("🇺🇸 US South", "us-south"),
    ]

    def __init__(self, channel: disnake.VoiceChannel):
        super().__init__(timeout=60)
        self.channel = channel
        options = [disnake.SelectOption(label=l, value=v) for l, v in self.REGIONS]
        menu = disnake.ui.StringSelect(placeholder="🌍 Регион...", custom_id="region_select", options=options[:25])
        menu.callback = self.callback
        self.add_item(menu)

    async def callback(self, inter: disnake.MessageInteraction):
        region = inter.data["values"][0]
        if not self.channel.permissions_for(inter.author).manage_channels:
            return await inter.response.send_message("❌ Нет прав!", ephemeral=True)
        try:
            await self.channel.edit(rtc_region=region)
            await inter.response.send_message(f"🌍 {region}", ephemeral=True)
        except:
            await inter.response.send_message("❌ Ошибка!", ephemeral=True)
        self.stop()


class VoiceRenameModal(disnake.ui.Modal):
    def __init__(self, service: VoiceService):
        self.service = service
        super().__init__(title="✏️ Переименовать", components=[disnake.ui.TextInput(label="Название", placeholder="Моя комната", custom_id="name", min_length=1, max_length=100)])

    async def callback(self, inter: disnake.ModalInteraction):
        vc = inter.author.voice.channel if inter.author.voice else None
        if not vc:
            return await inter.response.send_message("❌ Не в канале!", ephemeral=True)
        ok = await self.service.rename(vc, inter.text_values["name"], inter.author)
        await inter.response.send_message("✅ Готово!" if ok else "❌ Нет прав!", ephemeral=True)


class VoiceLimitModal(disnake.ui.Modal):
    def __init__(self, service: VoiceService):
        self.service = service
        super().__init__(title="👥 Лимит", components=[disnake.ui.TextInput(label="0 — без лимита", placeholder="0", custom_id="limit", min_length=1, max_length=2)])

    async def callback(self, inter: disnake.ModalInteraction):
        vc = inter.author.voice.channel if inter.author.voice else None
        if not vc:
            return await inter.response.send_message("❌ Не в канале!", ephemeral=True)
        try:
            limit = int(inter.text_values["limit"])
        except:
            return await inter.response.send_message("❌ Число!", ephemeral=True)
        ok = await self.service.limit(vc, limit, inter.author)
        await inter.response.send_message(f"👥 {limit if limit > 0 else 'без лимита'}" if ok else "❌ Нет прав!", ephemeral=True)


class VoiceInviteModal(disnake.ui.Modal):
    def __init__(self, service: VoiceService):
        self.service = service
        super().__init__(title="📩 Пригласить", components=[disnake.ui.TextInput(label="ID пользователя", placeholder="123456789", custom_id="user_id", min_length=1, max_length=20)])

    async def callback(self, inter: disnake.ModalInteraction):
        vc = inter.author.voice.channel if inter.author.voice else None
        if not vc:
            return await inter.response.send_message("❌ Не в канале!", ephemeral=True)
        raw = inter.text_values["user_id"].strip().replace("<@", "").replace(">", "").replace("!", "")
        try:
            target = inter.guild.get_member(int(raw))
            if not target:
                return await inter.response.send_message("❌ Не найден!", ephemeral=True)
        except:
            return await inter.response.send_message("❌ Неверный ID!", ephemeral=True)
        ok = await self.service.invite(vc, target, inter.author)
        await inter.response.send_message(f"✅ {target.mention}" if ok else "❌ Нет прав!", ephemeral=True)


class VoiceCog(commands.Cog):
    def __init__(self, bot: commands.Bot, service: VoiceService):
        self._bot = bot
        self._service = service
        self._trigger_id: Optional[int] = None
        self._bot.loop.create_task(self._on_start())

    async def _on_start(self):
        await self._bot.wait_until_ready()
        saved = await self._service.repo.get_config("trigger_id")
        if saved:
            self._trigger_id = int(saved)

    @commands.Cog.listener()
    async def on_voice_state_update(self, member: disnake.Member, before: disnake.VoiceState, after: disnake.VoiceState):
        if member.bot:
            return

        if after.channel and self._trigger_id and after.channel.id == self._trigger_id:
            existing = await self._service.repo.get_by_owner(member.id, member.guild.id)
            if existing:
                ch = member.guild.get_channel(existing["channel_id"])
                if ch and ch.id != after.channel.id:
                    try:
                        await member.move_to(ch)
                    except:
                        pass
                    return
            else:
                channel = await self._service.create(member, after.channel)
                if channel:
                    embed = disnake.Embed(title="🎛️ Управление комнатой", color=disnake.Color.green())
                    embed.add_field(name="👑 Владелец", value=member.mention, inline=True)
                    embed.set_footer(text="Меню снизу")
                    await channel.send(embed=embed, view=VoiceControlView(self._service))
            return

        if before.channel:
            room = await self._service.repo.get(before.channel.id)
            if room:
                if room["owner_id"] == member.id and len(before.channel.members) > 0:
                    await self._service.handle_owner_leave(before.channel, member)
                if len(before.channel.members) == 0:
                    await self._service.schedule_delete(before.channel)

        if after.channel:
            room = await self._service.repo.get(after.channel.id)
            if room:
                await self._service.cancel_delete(after.channel.id)

    @commands.slash_command(description="🎤 Голосовые комнаты")
    async def voice(self, inter: disnake.ApplicationCommandInteraction):
        pass

    @voice.sub_command(description="Установить триггер (админ)")
    async def set_trigger(self, inter: disnake.ApplicationCommandInteraction, канал: disnake.VoiceChannel):
        if not inter.author.guild_permissions.administrator:
            return await inter.response.send_message("❌ Только админ!", ephemeral=True)
        self._trigger_id = канал.id
        await self._service.repo.set_config("trigger_id", str(канал.id))
        await inter.response.send_message(f"✅ {канал.mention}", ephemeral=True)

    @voice.sub_command(description="Удалить триггер (админ)")
    async def remove_trigger(self, inter: disnake.ApplicationCommandInteraction):
        if not inter.author.guild_permissions.administrator:
            return await inter.response.send_message("❌ Только админ!", ephemeral=True)
        self._trigger_id = None
        await self._service.repo.set_config("trigger_id", "")
        await inter.response.send_message("✅ Удалён!", ephemeral=True)


def setup(bot: commands.Bot, service: VoiceService):
    bot.add_cog(VoiceCog(bot, service))
    logger.info("VoiceCog loaded")