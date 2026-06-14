from __future__ import annotations

import disnake
from disnake.ext import commands, tasks
from datetime import datetime, timedelta, timezone
from typing import Dict, Optional

from application.services.stats_service import StatsService
from infrastructure.logging import get_logger

logger = get_logger(__name__)

MSK = timezone(timedelta(hours=3))


class StatsCog(commands.Cog):
    """
    Ког для сбора и отображения статистики сервера.
    """

    def __init__(self, bot: commands.Bot, stats_service: StatsService):
        self._bot = bot
        self._service = stats_service
        self._voice_sessions: Dict[int, Dict[int, datetime]] = {}
        
        if self._service is not None:
            self._service.set_bot(bot)
        
        self._snapshot_task.start()
        logger.info("StatisticsCog initialized successful")

    def cog_unload(self):
        self._snapshot_task.cancel()

    @property
    def service(self) -> StatsService:
        return self._service

    @tasks.loop(hours=1)
    async def _snapshot_task(self):
        pass

    @_snapshot_task.before_loop
    async def _before_snapshot(self):
        await self._bot.wait_until_ready()

    @commands.Cog.listener()
    async def on_message(self, message: disnake.Message):
        await self._service.log_message(message)

    @commands.Cog.listener()
    async def on_voice_state_update(
        self,
        member: disnake.Member,
        before: disnake.VoiceState,
        after: disnake.VoiceState
    ):
        if member.bot or not member.guild:
            return

        guild_id = member.guild.id
        user_id = member.id

        if before.channel is None and after.channel is not None:
            self._voice_sessions.setdefault(guild_id, {})[user_id] = datetime.now(MSK)

        elif before.channel is not None and after.channel is None:
            joined_at = self._voice_sessions.get(guild_id, {}).pop(user_id, None)
            if joined_at:
                await self._service.log_voice_activity(member, joined_at)

        elif before.channel != after.channel:
            joined_at = self._voice_sessions.get(guild_id, {}).pop(user_id, None)
            if joined_at:
                await self._service.log_voice_activity(member, joined_at)
            self._voice_sessions.setdefault(guild_id, {})[user_id] = datetime.now(MSK)

    @commands.Cog.listener()
    async def on_member_join(self, member: disnake.Member):
        await self._service.log_member_join()

    @commands.Cog.listener()
    async def on_member_remove(self, member: disnake.Member):
        await self._service.log_member_leave()

    @commands.slash_command(description="📊 Статистика сервера и участников")
    async def stats(self, inter: disnake.ApplicationCommandInteraction):
        pass

    @stats.sub_command(description="Общая статистика сервера за 7 или 30 дней")
    async def server(
        self, 
        inter: disnake.ApplicationCommandInteraction, 
        period: int = commands.Param(7, choices=[7, 30])
    ):
        await inter.response.defer(ephemeral=True)
        
        data = await self._service.get_server_stats(inter.guild.id, period)
        
        embed = disnake.Embed(
            title=f"📈 Статистика сервера за {period} дней",
            color=disnake.Color.green()
        )
        
        # Основная статистика
        embed.add_field("💬 Всего сообщений", str(data["total_messages"]), inline=True)
        embed.add_field("👥 Активных участников", str(data["active_users"]), inline=True)
        embed.add_field("📝 Активных каналов", str(data["active_channels"]), inline=True)
        embed.add_field("📊 Среднее в день", f"{data['avg_per_day']} сообщений", inline=True)
        
        # Самый активный пользователь
        if data["top_user_id"]:
            top_user = inter.guild.get_member(data["top_user_id"])
            top_user_name = top_user.display_name if top_user else f"<@{data['top_user_id']}>"
            embed.add_field(
                "🏆 Самый активный", 
                f"{top_user_name} ({data['top_user_count']} сообщений)", 
                inline=True
            )
        
        # Самый активный канал
        if data["top_channel_id"]:
            channel = inter.guild.get_channel(data["top_channel_id"])
            channel_name = channel.mention if channel else f"<#{data['top_channel_id']}>"
            embed.add_field(
                "📝 Топ-канал", 
                f"{channel_name} ({data['top_channel_count']} сообщений)", 
                inline=True
            )
        
        # Пик активности
        if data["top_hour"] is not None:
            embed.add_field(
                "⏰ Пик активности", 
                f"{data['top_hour']}:00 ({data['top_hour_count']} сообщений)", 
                inline=True
            )
        
        # Активность по дням недели
        if data["daily_stats"]:
            daily_str = " ".join([f"{d['day']}: {d['count']}" for d in data["daily_stats"]])
            embed.add_field("📅 По дням недели", daily_str, inline=False)
        
        # Голосовая статистика
        embed.add_field("🎤 В голосе", f"{data['voice_users']} пользователей", inline=True)
        total_hours = round(data["total_voice_minutes"] / 60, 1)
        embed.add_field("⏱️ Часов в голосе", f"{total_hours} часов", inline=True)
        
        # Топ-3 по голосу
        if data["top_voice"]:
            voice_str = ""
            medals = ["🥇", "🥈", "🥉"]
            for i, v in enumerate(data["top_voice"]):
                member = inter.guild.get_member(v["user_id"])
                name = member.display_name if member else f"<@{v['user_id']}>"
                hours = round(v["voice_minutes"] / 60, 1)
                voice_str += f"{medals[i]} {name}: {hours}ч\n"
            embed.add_field("🎤 Топ-3 в голосе", voice_str, inline=False)
        
        embed.set_footer(text="Данные обновляются в реальном времени")
        await inter.edit_original_response(embed=embed)

    @stats.sub_command(description="Статистика участника")
    async def user(
        self, 
        inter: disnake.ApplicationCommandInteraction, 
        user: disnake.User = None
    ):
        await inter.response.defer(ephemeral=True)
        user = user or inter.author
        
        stats = await self._service.get_user_stats(user.id, inter.guild.id)
        
        if not stats:
            try:
                await self._service.stats_repo.get_or_create(user.id, inter.guild.id)
                stats = await self._service.get_user_stats(user.id, inter.guild.id)
            except:
                pass
        
        if not stats:
            return await inter.edit_original_response(
                f"❌ {user.display_name} ещё не отправлял сообщений на сервере."
            )

        embed = disnake.Embed(
            title=f"📊 {user.display_name}",
            color=disnake.Color.green()
        )
        embed.set_thumbnail(url=user.display_avatar.url)
        embed.add_field("💬 Сообщений", str(stats.get("messages_count", 0)), inline=True)
        embed.add_field("🎤 В голосе", f"{stats.get('voice_minutes', 0)} мин", inline=True)
        embed.add_field("⚠️ Предупреждений", str(stats.get("warnings_count", 0)), inline=True)
        
        if stats.get("last_message"):
            try:
                last_msg = datetime.fromisoformat(stats["last_message"])
                embed.add_field("🕒 Последнее сообщение", disnake.utils.format_dt(last_msg, "R"), inline=False)
            except:
                pass

        await inter.edit_original_response(embed=embed)

    @stats.sub_command(description="Топ-5 самых активных каналов за неделю")
    async def channels(self, inter: disnake.ApplicationCommandInteraction):
        await inter.response.defer(ephemeral=True)

        top = await self._service.get_top_channels(inter.guild.id, days=7, limit=5)
        if not top:
            return await inter.edit_original_response("Нет активных каналов.")

        desc = ""
        for i, row in enumerate(top, 1):
            channel = inter.guild.get_channel(row["channel_id"])
            name = channel.mention if channel else f"<#{row['channel_id']}>"
            desc += f"{i}. {name} — {row['count']} сообщений\n"

        embed = disnake.Embed(title="🏆 Топ-5 каналов", description=desc, color=disnake.Color.orange())
        await inter.edit_original_response(embed=embed)

    @stats.sub_command(description="График активности по часам (последние 7 дней)")
    async def activity(self, inter: disnake.ApplicationCommandInteraction):
        await inter.response.defer(ephemeral=True)

        hourly = await self._service.get_activity_by_hour(inter.guild.id, days=7)
        counts = [h["count"] for h in hourly]
        max_count = max(counts) if counts else 1
        
        if max_count == 0:
            return await inter.edit_original_response("📊 Нет активности за последние 7 дней.")
        
        bar_length = 12
        graph = ""
        for item in hourly:
            h = item["hour"]
            count = item["count"]
            bars = "🟩" * max(1, count * bar_length // max_count) if count > 0 else "⬛"
            graph += f"`{h}:00` {bars} {count}\n"

        embed = disnake.Embed(
            title="📊 Активность по часам (7 дней, МСК)",
            description=graph,
            color=disnake.Color.purple()
        )
        embed.set_footer(text="🟩 — активность, масштаб относительный | ⬛ — нет сообщений")
        await inter.edit_original_response(embed=embed)

    @commands.slash_command(description="🏆 Топ-10 самых активных участников за неделю")
    async def leaderboard(self, inter: disnake.ApplicationCommandInteraction):
        await inter.response.defer(ephemeral=True)
        
        top = await self._service.get_leaderboard(inter.guild.id, days=7, limit=10)
        
        if not top:
            return await inter.edit_original_response("📊 Нет данных. Напишите что-нибудь в чат!")
        
        embed = disnake.Embed(title="🏆 Топ-10 активных участников (7 дней)", color=disnake.Color.gold())
        medals = ["🥇", "🥈", "🥉"] + [f"{i}." for i in range(4, 11)]
        
        for i, row in enumerate(top):
            user_id = row["user_id"]
            count = row["count"]
            
            member = inter.guild.get_member(user_id)
            if not member:
                try:
                    member = await self._bot.fetch_user(user_id)
                except:
                    pass
            
            name = member.display_name if member else f"Неизвестный ({user_id})"
            medal = medals[i] if i < len(medals) else f"{i+1}."
            
            embed.add_field(name=f"{medal} {name}", value=f"💬 {count} сообщений", inline=False)
        
        await inter.edit_original_response(embed=embed)


def setup(bot: commands.Bot, stats_service: StatsService):
    bot.add_cog(StatsCog(bot, stats_service))
    logger.info("StatsCog loaded")