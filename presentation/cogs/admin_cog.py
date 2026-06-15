from datetime import datetime, timedelta, timezone
import asyncio
import random
import importlib
import sys

import disnake
from disnake.ext import commands

from application.services.role_service import RoleService
from application.services.admin_service import AdminService
from infrastructure.logging import get_logger
from presentation.views import RolePanelView, RolePanelPaginatedView

logger = get_logger(__name__)

class WarnModal(disnake.ui.Modal):
    def __init__(self, cog, target_user: disnake.User):
        self.cog = cog
        self.target_user = target_user

        components = [
            disnake.ui.TextInput(
                label="Причина предупреждения",
                placeholder="Например: Спам, оскорбления...",
                custom_id="warn_reason",
                style=disnake.TextInputStyle.paragraph,
                max_length=200,
                required=True
            )
        ]
        super().__init__(title=f"Варн для {target_user.name}", components=components)
    async def callback(self, inter: disnake.ModalInteraction):
        reason = inter.text_values["warn_reason"]
        await self.cog.warn(ctx=inter, user=self.target_user, reason=reason)

class MuteModal(disnake.ui.Modal):
    def __init__(self, cog, target_user: disnake.User):
        self.cog = cog
        self.target_user = target_user

        components = [
            disnake.ui.TextInput(
                label="Причина мьюта",
                placeholder="Например: Спам, оскорбления...",
                custom_id="mute_reason",
                style=disnake.TextInputStyle.paragraph,
                max_length=200,
                required=True
            ),
            disnake.ui.TextInput(
                label="Срок мьюта (Часы)",
                placeholder="Например: 1, 2, 3...",
                custom_id="mute_duration_hours",
                style=disnake.TextInputStyle.paragraph,
                max_length=200,
                required=True
            ),
            disnake.ui.TextInput(
                label="Срок мьюта (Минуты)",
                placeholder="Например: 15, 20, 30...",
                custom_id="mute_duration_minutes",
                style=disnake.TextInputStyle.paragraph,
                max_length=200,
                required=True
            )
        ]
        super().__init__(title=f"Мьют для {target_user.name}", components=components)
    async def callback(self, inter: disnake.ModalInteraction):
        reason = inter.text_values["mute_reason"]
        duration_hours = int(inter.text_values["mute_duration_hours"])
        duration_munites = int(inter.text_values["mute_duration_minutes"])
        await self.cog.mute(ctx=inter, user=self.target_user, reason=reason, hours=duration_hours, minutes=duration_munites)


class AdminCog(commands.Cog):
    def __init__(self, bot: commands.Bot, role_service: RoleService, admin_service: AdminService):
        self._bot = bot
        self._role_service = role_service
        self._admin_service = admin_service
        self.dev = False  
        logger.info("AdminCog initialized")

    async def warn(self, user: disnake.User, reason: str, ctx):
        if not ctx.author.guild_permissions.administrator:
            await ctx.response.send_message("Только администраторы могут использовать эту команду", ephemeral=True)
            return
        else:
            try:
                # Логируем предупреждение в БД
                await self._admin_service.log_warning(
                    user_id=user.id,
                    mod_id=ctx.author.id,
                    reason=reason
                )
                await ctx.response.send_message(f"{ctx.author.mention} Выдал предупреждение пользователю {user.mention} по причине: {reason}")
            except Exception as e:
                logger.error(f"Error logging warning: {e}")
                await ctx.response.send_message(f"❌ Ошибка при логировании предупреждения: {str(e)}", ephemeral=True)

    @commands.slash_command(name="warn", description="Выдать предупреждение участнику")
    async def slash_warn(self, user: disnake.User, reason: str, ctx: disnake.ApplicationCommandInteraction):
        await self.warn(user, reason, ctx)

    @commands.user_command(name="Выдать варн")
    async def apps_warn(self, ctx: disnake.UserCommandInteraction):
        # Открываем модалку. Внутрь передаем сам Ког (self) и цель (ctx.target)
        await ctx.response.send_modal(modal=WarnModal(self, ctx.target))

    @commands.slash_command(name="kick", description="Исключить участника с сервера")
    async def kick(self, user: disnake.User, reason: str, ctx: disnake.ApplicationCommandInteraction):
        if not ctx.author.guild_permissions.administrator:
            await ctx.response.send_message("Только администраторы могут использовать эту команду", ephemeral=True)
            return
        else:
            try:
                await user.kick(reason=reason)
                
                # Логируем кик в БД
                await self._admin_service.log_kick(
                    user_id=user.id,
                    mod_id=ctx.author.id,
                    reason=reason
                )
                
                await ctx.response.send_message(f"{ctx.author.mention} Исключил пользователя {user.mention} по причине: {reason}")
            except disnake.Forbidden:
                await ctx.response.send_message("❌ Я не могу исключить этого пользователя. У меня нет прав!", ephemeral=True)
            except Exception as e:
                logger.error(f"Error kicking user: {e}")
                await ctx.response.send_message(f"❌ Ошибка при исключении пользователя: {str(e)}", ephemeral=True)
    
    @commands.slash_command(name="ban", description="Забанить участника")
    async def ban(self, user: disnake.User, reason: str, days_clean: int, ctx: disnake.ApplicationCommandInteraction):
        if not ctx.author.guild_permissions.administrator:
            await ctx.response.send_message("Только администраторы могут использовать эту команду", ephemeral=True)
            return
        else:
            try:
                await user.ban(reason=reason, delete_message_days=days_clean)
                
                # Логируем бан в БД
                await self._admin_service.log_ban(
                    user_id=user.id,
                    mod_id=ctx.author.id,
                    reason=reason
                )
                
                await ctx.response.send_message(f"{ctx.author.mention} Забанил пользователя {user.mention} по причине: {reason}. Удалил сообщения за {days_clean} дней")
            except disnake.Forbidden:
                await ctx.response.send_message("❌ Я не могу забанить этого пользователя. У меня нет прав!", ephemeral=True)
            except Exception as e:
                logger.error(f"Error banning user: {e}")
                await ctx.response.send_message(f"❌ Ошибка при бане пользователя: {str(e)}", ephemeral=True)
    
    @commands.slash_command(name="unban", description="Разбанить участника")
    async def unban(self, user: disnake.User, reason: str, ctx: disnake.ApplicationCommandInteraction):
        if not ctx.author.guild_permissions.administrator:
            await ctx.response.send_message("Только администраторы могут использовать эту команду", ephemeral=True)
            return
        else:
            try:
                user = await self._bot.fetch_user(int(user.id))
                await ctx.guild.unban(user, reason=reason)
                
                # Логируем разбан в БД
                await self._admin_service.log_unban(
                    user_id=user.id,
                    mod_id=ctx.author.id,
                    reason=reason
                )
                
                await ctx.response.send_message(f"{ctx.author.mention} Разбанил пользователя {user.mention} по причине: {reason}")
            except disnake.Forbidden:
                await ctx.response.send_message("❌ Я не могу разбанить этого пользователя. У меня нет прав!", ephemeral=True)
            except Exception as e:
                logger.error(f"Error unbanning user: {e}")
                await ctx.response.send_message(f"❌ Ошибка при разбане пользователя: {str(e)}", ephemeral=True)

    async def mute(self, user: disnake.User, reason: str, hours: int, minutes: int,
ctx):
        if not ctx.author.guild_permissions.administrator:
            await ctx.response.send_message("Только администраторы могут использовать эту команду", ephemeral=True)
            return
        else:
            try:
                duration = timedelta(hours=hours, minutes=minutes)
                await user.timeout(duration=duration, reason=reason)
                
                # Логируем мьют в БД
                await self._admin_service.log_mute(
                    user_id=user.id,
                    mod_id=ctx.author.id,
                    hours=hours,
                    minutes=minutes,
                    reason=reason
                )
                
                await ctx.response.send_message(f"{ctx.author.mention} Выдал тайм-аут пользователю {user.mention} по причине: {reason}, на {hours} часов и {minutes} минут")
            except disnake.Forbidden:
                await ctx.response.send_message("Я не могу выдать тайм-аут этому пользователю. У меня нет прав!", ephemeral=True)
            except Exception as e:
                logger.error(f"Error muting user: {e}")
                await ctx.response.send_message(f"❌ Ошибка при выдаче тайм-аута: {str(e)}", ephemeral=True)

    @commands.slash_command(name="mute", description="Выдать тайм-аут участнику")
    async def slash_mute(self, ctx: disnake.ApplicationCommandInteraction, user: disnake.User, reason: str, hours: int, minutes: int = 0):
        await self.mute(user, reason, hours, minutes, ctx)

    @commands.user_command(name="Выдать тайм-аут")
    async def apps_mute(self, ctx: disnake.UserCommandInteraction):
        # Открываем модалку. Внутрь передаем сам Ког (self) и цель (ctx.target)
        await ctx.response.send_modal(modal=MuteModal(self, ctx.target))

    @commands.slash_command(name="unmute", description="Размутить участника")
    async def unmute(self, user: disnake.User, reason: str,
        ctx: disnake.ApplicationCommandInteraction):
            if not ctx.author.guild_permissions.administrator:
                await ctx.response.send_message("Только администраторы могут использовать эту команду", ephemeral=True)
                return
            else:
                try:
                    await user.timeout(duration=None, reason=reason)
                    
                    # Логируем размут в БД
                    await self._admin_service.log_unmute(
                        user_id=user.id,
                        mod_id=ctx.author.id,
                        reason=reason
                    )
                    
                    await ctx.response.send_message(f"{ctx.author.mention} Размутил пользователя {user.mention} по причине: {reason}")
                except disnake.Forbidden:
                    await ctx.response.send_message("Я не могу размутить этого пользователя. У меня нет прав!", ephemeral=True)
                except Exception as e:
                    logger.error(f"Error unmuting user: {e}")
                    await ctx.response.send_message(f"❌ Ошибка при размуте пользователя: {str(e)}", ephemeral=True)

    @commands.slash_command(name="history", description="Посмотреть историю нарушений пользователя")
    async def history(self, user: disnake.User, ctx: disnake.ApplicationCommandInteraction):
        
        try:
            await ctx.response.defer()
            
            # Получаем сводку нарушений
            summary = await self._admin_service.get_violations_summary(user.id)
            violations = await self._admin_service.get_user_violations(user.id)
            
            # Формируем embed
            embed = disnake.Embed(
                title=f"📋 Нарушения пользователя {user.name}",
                description=f"ID пользователя: {user.id}",
                color=disnake.Color.orange() if summary["active"] > 0 else disnake.Color.green()
            )
            
            # Добавляем информацию о количестве нарушений
            embed.add_field(
                name="📊 Статистика",
                value=f"**Всего нарушений:** {summary['total']}\n**Активных наказаний:** {summary['active']}",
                inline=False
            )
            
            # Добавляем информацию о типах нарушений
            if summary["by_type"]:
                by_type_text = "\n".join([f"• {ptype}: {count}" for ptype, count in summary["by_type"].items()])
                embed.add_field(
                    name="⚠️ Активные наказания по типам",
                    value=by_type_text,
                    inline=False
                )
            
            # Добавляем последние нарушения (максимум 5)
            if violations:
                violations_text = ""
                for violation in violations[:5]:
                    violation_type = violation["type"].upper()
                    violation_date = violation["timestamp"]
                    violation_reason = violation["reason"] or "Не указана"
                    violations_text += f"**{violation_type}** - {violation_date}\n"
                    violations_text += f"Причина: {violation_reason}\n"
                    if violation["duration"]:
                        violations_text += f"Длительность: {violation['duration']}\n"
                    violations_text += "\n"
                
                embed.add_field(
                    name="📝 Последние нарушения",
                    value=violations_text[:1024],  # Ограничение длины поля
                    inline=False
                )
            else:
                embed.add_field(
                    name="✅ Статус",
                    value="У пользователя нет записей о нарушениях",
                    inline=False
                )
            
            embed.set_footer(text=f"Запрошено: {ctx.author.name}", icon_url=ctx.author.avatar.url)
            embed.timestamp = datetime.now()
            
            await ctx.edit_original_response(embed=embed)
            
        except Exception as e:
            logger.error(f"Error getting violations: {e}")
            await ctx.edit_original_response(content=f"❌ Ошибка при получении информации о нарушениях: {str(e)}")

    @commands.user_command(name="Показать историю нарушений")
    async def user_history_command(self, ctx: disnake.UserCommandInteraction):
        if not ctx.author.guild_permissions.administrator:
            await ctx.response.send_message("Только администраторы могут использовать эту команду", ephemeral=True)
            return
        
        try:
            await ctx.response.defer()
            
            target_user = ctx.target
            
            # Получаем сводку нарушений
            summary = await self._admin_service.get_violations_summary(target_user.id)
            violations = await self._admin_service.get_user_violations(target_user.id)
            
            # Формируем embed
            embed = disnake.Embed(
                title=f"📋 Нарушения пользователя {target_user.name}",
                description=f"ID пользователя: {target_user.id}",
                color=disnake.Color.orange() if summary["active"] > 0 else disnake.Color.green()
            )
            
            # Добавляем информацию о количестве нарушений
            embed.add_field(
                name="📊 Статистика",
                value=f"**Всего нарушений:** {summary['total']}\n**Активных наказаний:** {summary['active']}",
                inline=False
            )
            
            # Добавляем информацию о типах нарушений
            if summary["by_type"]:
                by_type_text = "\n".join([f"• {ptype}: {count}" for ptype, count in summary["by_type"].items()])
                embed.add_field(
                    name="⚠️ Активные наказания по типам",
                    value=by_type_text,
                    inline=False
                )
            
            # Добавляем последние нарушения (максимум 5)
            if violations:
                violations_text = ""
                for violation in violations[:5]:
                    violation_type = violation["type"].upper()
                    violation_date = violation["timestamp"]
                    violation_reason = violation["reason"] or "Не указана"
                    violations_text += f"**{violation_type}** - {violation_date}\n"
                    violations_text += f"Причина: {violation_reason}\n"
                    if violation["duration"]:
                        violations_text += f"Длительность: {violation['duration']}\n"
                    violations_text += "\n"
                
                embed.add_field(
                    name="📝 Последние нарушения",
                    value=violations_text[:1024],  # Ограничение длины поля
                    inline=False
                )
            else:
                embed.add_field(
                    name="✅ Статус",
                    value="У пользователя нет записей о нарушениях",
                    inline=False
                )
            
            embed.set_footer(text=f"Запрошено: {ctx.author.name}", icon_url=ctx.author.avatar.url)
            embed.timestamp = datetime.now()
            
            await ctx.edit_original_response(embed=embed)
            
        except Exception as e:
            logger.error(f"Error getting violations: {e}")
            await ctx.edit_original_response(content=f"❌ Ошибка при получении информации о нарушениях: {str(e)}")

    @commands.slash_command(name="bot", description="Команды управления ботом")
    async def admin_bot(self, ctx: disnake.ApplicationCommandInteraction):
        pass

    @admin_bot.sub_command(name="reload", description="Перезагрузить модули без рестарта бота")
    async def reload(self, ctx: disnake.ApplicationCommandInteraction):
        if not ctx.author.guild_permissions.administrator:
            await ctx.response.send_message("Только администраторы могут использовать эту команду", ephemeral=True)
            return
        
        try:
            await ctx.response.defer()
            
            cogs_to_reload = list(self._bot.cogs.keys())
            
            if not cogs_to_reload:
                await ctx.edit_original_response(content="Нет загруженных модулей для перезагрузки")
                return
            
            reloaded = []
            failed = []
            
            for cog_name in cogs_to_reload:
                try:
                    try:
                        module_name = cog_name.lower()
                        if not module_name.endswith("_cog"):
                            module_name = module_name + "_cog"
                        
                        self._bot.reload_extension(f"presentation.cogs.{module_name}")
                    except Exception as reload_error:
                        logger.debug(f"reload_extension failed for {cog_name}, trying alternative method: {reload_error}")
                        
                        self._bot.remove_cog(cog_name)

                        if cog_name == "AdminCog":
                            from presentation.cogs.admin_cog import AdminCog
                            importlib.reload(sys.modules['presentation.cogs.admin_cog'])
                            self._bot.add_cog(AdminCog(self._bot, self._role_service, self._admin_service))
                        elif cog_name == "RolesCog":
                            from presentation.cogs.roles_cog import RolesCog
                            importlib.reload(sys.modules['presentation.cogs.roles_cog'])
                            self._bot.add_cog(RolesCog(self._bot, self._role_service))
                    
                    reloaded.append(cog_name)
                    logger.info(f"Reloaded cog: {cog_name}")
                except Exception as e:
                    failed.append((cog_name, str(e)))
                    logger.error(f"Failed to reload cog {cog_name}: {e}")
            
            # Формируем ответ
            embed = disnake.Embed(
                title="🔄 Перезагрузка модулей",
                description="",
                color=disnake.Color.green() if not failed else disnake.Color.orange()
            )
            
            if reloaded:
                embed.add_field(
                    name="✅ Успешно перезагруженные модули",
                    value="\n".join(reloaded),
                    inline=False
                )
            
            if failed:
                failed_text = "\n".join([f"• {name}: {error}" for name, error in failed])
                embed.add_field(
                    name="❌ Ошибки при перезагрузке",
                    value=failed_text,
                    inline=False
                )
            
            embed.set_footer(text=f"Перезагружено: {len(reloaded)}/{len(cogs_to_reload)}")
            
            await ctx.edit_original_response(embed=embed)
            
        except Exception as e:
            logger.error(f"Error reloading cogs: {e}")
            await ctx.edit_original_response(content=f"❌ Ошибка при перезагрузке: {str(e)}")

    @admin_bot.sub_command(name="status", description="Статус всех модулей и задач")
    async def status(self, ctx: disnake.ApplicationCommandInteraction):
        if not ctx.author.guild_permissions.administrator:
            await ctx.response.send_message("Только администраторы могут использовать эту команду", ephemeral=True)
            return
        
        try:
            await ctx.response.defer()

            embed = disnake.Embed(
                title="📊 Статус бота",
                color=disnake.Color.blue()
            )

            embed.add_field(
                name="🔌 Подключение",
                value=f"{'✅ Подключен' if self._bot.is_ready() else '❌ Отключен'}",
                inline=True
            )

            embed.add_field(
                name="⏱️ Ping",
                value=f"{round(self._bot.latency * 1000)}ms",
                inline=True
            )

            cogs = list(self._bot.cogs.keys())
            embed.add_field(
                name=f"📦 Загруженные модули ({len(cogs)})",
                value="\n".join([f"• {cog}" for cog in cogs]) if cogs else "Нет модулей",
                inline=False
            )

            if self._bot.guilds:
                guild = self._bot.guilds[0]
                embed.add_field(
                    name="🏢 Сервер",
                    value=f"**Название:** {guild.name}\n**ID:** {guild.id}\n**Участников:** {guild.member_count}",
                    inline=False
                )

            tasks = [task for task in asyncio.all_tasks() if not task.done()]
            if tasks:
                if self.dev:
                    # Подробный список задач
                    tasks_display = []
                    for i, task in enumerate(tasks[:10]):
                        task_name = task.get_name()
                        tasks_display.append(f"• {task_name}")
                    
                    tasks_text = "\n".join(tasks_display)
                    if len(tasks) > 10:
                        tasks_text += f"\n... и еще {len(tasks) - 10}"
                else:
                    # Только текст без списка
                    tasks_text = f"Активно {len(tasks)} задач"
                
                embed.add_field(
                    name=f"⚙️ Активные задачи ({len(tasks)})",
                    value=tasks_text,
                    inline=False
                )
            else:
                embed.add_field(
                    name="⚙️ Активные задачи (0)",
                    value="Нет активных задач",
                    inline=False
                )
            
            embed.set_footer(text=f"Время: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}")
            
            await ctx.edit_original_response(embed=embed)
            
        except Exception as e:
            logger.error(f"Error getting bot status: {e}")
            await ctx.edit_original_response(content=f"❌ Ошибка при получении статуса: {str(e)}")

    @commands.slash_command(name="slowmode", description="Установить замедленный режим для канала")
    async def slowmode(self, channel: disnake.TextChannel, seconds: int = 0, ctx: disnake.ApplicationCommandInteraction = None):
        if not ctx.author.guild_permissions.administrator:
            await ctx.response.send_message("Только администраторы могут использовать эту команду", ephemeral=True)
            return
        
        try:
            # Проверяем, что значение в допустимом диапазоне (0-21600 секунд = 0-6 часов)
            if seconds < 0 or seconds > 21600:
                await ctx.response.send_message("❌ Значение должно быть от 0 до 21600 секунд (6 часов)", ephemeral=True)
                return
            
            await channel.edit(slowmode_delay=seconds)
            
            if seconds == 0:
                await ctx.response.send_message(f"✅ Замедленный режим отключен для канала {channel.mention}")
            else:
                await ctx.response.send_message(f"✅ Замедленный режим для канала {channel.mention} установлен на {seconds} секунд")
                
        except disnake.Forbidden:
            await ctx.response.send_message("❌ У меня нет прав для изменения настроек канала!", ephemeral=True)
        except Exception as e:
            logger.error(f"Error setting slowmode: {e}")
            await ctx.response.send_message(f"❌ Ошибка при установке замедленного режима: {str(e)}", ephemeral=True)

    @commands.slash_command(name="purge", description="Массовое удаление сообщений")
    async def purge(
        self, 
        ctx: disnake.ApplicationCommandInteraction,
        limit: int = 100,
        user: disnake.User = None,
        contains: str = None
    ):
        if not ctx.author.guild_permissions.administrator:
            await ctx.response.send_message("Только администраторы могут использовать эту команду", ephemeral=True)
            return
        
        # Проверяем адекватность лимита (Discord позволяет просматривать сколько угодно, но лучше поставить рамки)
        if limit < 1 or limit > 500:
            await ctx.response.send_message("❌ Лимит должен быть от 1 до 500 сообщений", ephemeral=True)
            return

        try:
            # Откладываем ответ, так как поиск по 500 сообщениям может занять пару секунд
            await ctx.response.defer(ephemeral=True)
            
            # Создаем функцию-фильтр для purge
            def purge_check(message: disnake.Message) -> bool:
                # Фильтр по пользователю
                if user is not None and message.author.id != user.id:
                    return False
                
                # Фильтр по тексту
                if contains is not None and contains.lower() not in message.content.lower():
                    return False
                
                return True

            # Запускаем быстрое удаление через встроенный метод
            # Он сам проигнорирует сообщения старше 14 дней
            deleted_messages = await ctx.channel.purge(limit=limit, check=purge_check)
            deleted_count = len(deleted_messages)
            
            # Формируем красивый ответ
            embed = disnake.Embed(
                title="🗑️ Очистка канала завершена",
                color=disnake.Color.green(),
                timestamp=disnake.utils.utcnow()
            )
            
            embed.add_field(
                name="📊 Результаты",
                value=f"**Удалено сообщений:** {deleted_count}\n*(Сообщения старше 14 дней не подлежат массовому удалению)*",
                inline=False
            )
            
            # Добавляем информацию об использованных фильтрах
            filters_info = []
            if user:
                filters_info.append(f"👤 Пользователь: {user.mention}")
            if contains:
                filters_info.append(f"🔍 Содержит: \"{contains}\"")
            
            if filters_info:
                embed.add_field(
                    name="⚙️ Использованные фильтры",
                    value="\n".join(filters_info),
                    inline=False
                )
            
            embed.set_footer(text=f"Выполнено администратором: {ctx.author.name}", icon_url=ctx.author.avatar.url)
            
            # Изменяем наш defer-ответ на готовый эмбед
            await ctx.edit_original_response(embed=embed)
            
            # Логирование (если переменная logger создана у тебя в проекте)
            if 'logger' in globals() or hasattr(self, 'logger'):
                logger.info(f"Purge executed by {ctx.author.name}: deleted {deleted_count} messages")
                
        except disnake.Forbidden:
            await ctx.edit_original_response(content="❌ У меня нет прав `Управление сообщениями` в этом канале!")
        except Exception as e:
            await ctx.edit_original_response(content=f"❌ Ошибка при удалении сообщений: {str(e)}")

def setup(bot: commands.Bot):
    """Установка кога (для классической загрузки)"""
    pass