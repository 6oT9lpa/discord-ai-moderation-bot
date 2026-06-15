import disnake
from disnake.ext import commands, tasks
from typing import Optional
import asyncio

from application.services.ai_service import AIService
from application.services.admin_service import AdminService
from infrastructure.database.connection import DatabaseManager
from infrastructure.logging import get_logger

logger = get_logger(__name__)


class AICog(commands.Cog):
    """
    Cog для управления ИИ функциями
    """
    
    def __init__(self, bot: commands.Bot, ai_service: AIService, admin_service: AdminService, db: DatabaseManager):
        self.bot = bot
        self.ai_service = ai_service
        self.admin_service = admin_service
        self.db = db
        self.message_queue = asyncio.Queue()
        self.ai_threshold = 0.85
        
        # Запускаем фоновый воркер
        self.process_messages.start()
        
        logger.info("AICog initialized")

    def cog_unload(self):
        self.process_messages.cancel()
    
    @commands.slash_command(
        name="ai_chat",
        description="Общайтесь с ИИ ассистентом"
    )
    async def ai_chat(
        self,
        inter: disnake.ApplicationCommandInteraction,
        message: str = commands.Param(description="Ваше сообщение для ИИ", max_length=1000)
    ):
        """
        Команда для чата с ИИ
        """
        await inter.response.defer()
        
        try:
            user_id = inter.author.id
            username = inter.author.name
            
            # Получить роли пользователя
            roles = []
            if inter.author.roles:
                roles = [role.name for role in inter.author.roles if role.name != "@everyone"]
            
            # Информация о пользователе для ИИ
            user_info = {
                "id": user_id,
                "username": username,
                "roles": roles,
                "is_admin": inter.author.guild_permissions.administrator if inter.author else False
            }
            
            # Генерировать ответ от ИИ
            response = await self.ai_service.chat(
                user_id=user_id,
                message=message,
                user_info=user_info,
                use_history=True
            )
            
            if response is None:
                await inter.edit_original_response(
                    embed=disnake.Embed(
                        title="❌ Ошибка",
                        description="Не удалось получить ответ от ИИ. Убедитесь, что Ollama запущена на http://localhost:11434",
                        color=disnake.Color.red()
                    )
                )
                return
            
            # Обрезать ответ если он слишком длинный (макс 2000 символов для Discord)
            if len(response) > 1900:
                response = response[:1900] + "..."
            
            embed = disnake.Embed(
                title="🤖 Ответ ИИ",
                description=response,
                color=disnake.Color.blue()
            )
            embed.add_field(
                name="👤 Пользователь",
                value=f"`{username}`",
                inline=True
            )
            if roles:
                embed.add_field(
                    name="🏷️ Роли",
                    value=f"`{', '.join(roles)}`",
                    inline=True
                )
            embed.set_footer(text=f"ID: {user_id}")
            
            await inter.edit_original_response(embed=embed)
            
        except Exception as e:
            logger.error(f"Error in ai_chat: {e}", exc_info=True)
            await inter.edit_original_response(
                embed=disnake.Embed(
                    title="❌ Ошибка",
                    description=f"Произошла ошибка: {str(e)[:100]}",
                    color=disnake.Color.red()
                )
            )
    
    @commands.slash_command(
        name="ai_clear",
        description="Очистить историю беседы"
    )
    async def ai_clear(self, inter: disnake.ApplicationCommandInteraction):
        """
        Очистить историю беседы пользователя
        """
        user_id = inter.author.id
        self.ai_service.clear_conversation(user_id)
        
        embed = disnake.Embed(
            title="✅ История очищена",
            description="Ваша история беседы с ИИ была очищена. Начните новый разговор!",
            color=disnake.Color.green()
        )
        await inter.response.send_message(embed=embed, ephemeral=True)
    
    @commands.slash_command(
        name="ai_history",
        description="Показать историю беседы"
    )
    async def ai_history(self, inter: disnake.ApplicationCommandInteraction):
        """
        Показать историю беседы пользователя
        """
        user_id = inter.author.id
        history = self.ai_service.get_conversation_history(user_id)
        
        if not history:
            embed = disnake.Embed(
                title="📝 История пуста",
                description="У вас пока нет беседы с ИИ. Начните с команды /ai_chat",
                color=disnake.Color.yellow()
            )
            await inter.response.send_message(embed=embed, ephemeral=True)
            return
        
        # Форматировать историю
        history_text = ""
        for msg in history[-10:]:  # Показать последние 10 сообщений
            role = "👤 Вы" if msg["role"] == "user" else "🤖 ИИ"
            content = msg["content"][:100]  # Обрезать длинные сообщения
            if len(msg["content"]) > 100:
                content += "..."
            history_text += f"\n**{role}:** {content}\n"
        
        embed = disnake.Embed(
            title="📝 История беседы",
            description=history_text if history_text else "История пуста",
            color=disnake.Color.blue()
        )
        embed.set_footer(text=f"Всего сообщений: {len(history)}")
        
        await inter.response.send_message(embed=embed, ephemeral=True)
    
    @commands.slash_command(
        name="ai_stats",
        description="Показать статистику модерации"
    )
    async def ai_stats(self, inter: disnake.ApplicationCommandInteraction):
        """
        Показать статистику срабатываний модерации
        """
        stats = self.ai_service.get_stats()
        
        embed = disnake.Embed(
            title="📊 Статистика модерации",
            description="Статистика срабатываний ИИ модерации",
            color=disnake.Color.blue()
        )
        embed.add_field(
            name="🚫 Спам обнаружен",
            value=f"`{stats['spam_detected']}`",
            inline=True
        )
        embed.add_field(
            name="⚔️ Насилие обнаружено",
            value=f"`{stats['violence_detected']}`",
            inline=True
        )
        embed.add_field(
            name="⚠️ Опасный контент",
            value=f"`{stats['safety_detected']}`",
            inline=True
        )
        embed.add_field(
            name="🕐 Последний сброс",
            value=f"`{stats['last_reset']}`",
            inline=False
        )
        
        await inter.response.send_message(embed=embed, ephemeral=True)
    
    @commands.slash_command(
        name="ai_test",
        description="Протестировать Ollama подключение"
    )
    async def ai_test(self, inter: disnake.ApplicationCommandInteraction):
        """
        Протестировать подключение к Ollama
        """
        await inter.response.defer()
        
        try:
            ollama_client = self.ai_service._ollama
            connection_ok = await ollama_client.check_connection()
            
            if connection_ok:
                embed = disnake.Embed(
                    title="✅ Ollama подключена",
                    description=f"**Модель:** {ollama_client.model}\n**URL:** {ollama_client.base_url}",
                    color=disnake.Color.green()
                )
            else:
                embed = disnake.Embed(
                    title="❌ Ollama не подключена",
                    description=f"Не удается подключиться к Ollama на {ollama_client.base_url}\n\n"
                               f"**Как установить:**\n"
                               f"1. Скачайте Ollama: https://ollama.ai\n"
                               f"2. Запустите: `ollama serve`\n"
                               f"3. В другом терминале: `ollama pull {ollama_client.model}`",
                    color=disnake.Color.red()
                )
            
            await inter.edit_original_response(embed=embed)
            
        except Exception as e:
            logger.error(f"Error in ai_test: {e}", exc_info=True)
            await inter.edit_original_response(
                embed=disnake.Embed(
                    title="❌ Ошибка",
                    description=f"Произошла ошибка при тестировании: {str(e)}",
                    color=disnake.Color.red()
                )
            )
    
    @commands.Cog.listener()
    async def on_message(self, message: disnake.Message):
        if message.author.bot or not message.guild:
            return
            
        row = await self.db.fetch_one("SELECT is_ai_whitelisted FROM channel_config WHERE channel_id = ?", (message.channel.id,))
        if row and row['is_ai_whitelisted']:
            return
            
        await self.message_queue.put(message)

    @tasks.loop(seconds=1)
    async def process_messages(self):
        try:
            for _ in range(5):
                if self.message_queue.empty():
                    break
                message = await self.message_queue.get()
                await self._moderate_message(message)
                self.message_queue.task_done()
        except Exception as e:
            logger.error(f"Error in process_messages worker: {e}", exc_info=True)

    @process_messages.before_loop
    async def before_process_messages(self):
        await self.bot.wait_until_ready()

    async def _moderate_message(self, message: disnake.Message):
        content = message.content
        if not content:
            return

        logger.info(f"[AI Moderation] Проверка сообщения {message.id} от {message.author}: '{content[:50]}...'")

        spam_res = await self.ai_service.classify_spam(content)
        if spam_res:
            spam_type = spam_res.get("type")
            conf = float(spam_res.get("confidence", 0.0))
            if spam_type in ["SPAM", "AD", "INVITE"] and conf > self.ai_threshold:
                reason = spam_res.get("reason", "Обнаружен спам/реклама")
                logger.warning(f"[AI Moderation] Нарушение (SPAM): {spam_type} - {reason} (Уверенность: {conf})")
                await self._handle_violation(message, "spam", reason)
                return
            else:
                logger.info(f"[AI Moderation] SPAM проверка пройдена: {spam_type} (Уверенность: {conf})")
        else:
            logger.info("[AI Moderation] SPAM проверка не вернула результат")

        viol_res = await self.ai_service.classify_violence(content)
        if viol_res:
            viol_type = viol_res.get("type")
            conf = float(viol_res.get("confidence", 0.0))
            if viol_type in ["VIOLENCE", "BULLYING", "NSFW"] and conf > self.ai_threshold:
                reason = viol_res.get("reason", "Обнаружен опасный контент")
                logger.warning(f"[AI Moderation] Нарушение (VIOLENCE): {viol_type} - {reason} (Уверенность: {conf})")
                await self._handle_violation(message, "violence", reason, heavy=True)
                return
            else:
                logger.info(f"[AI Moderation] VIOLENCE проверка пройдена: {viol_type} (Уверенность: {conf})")
        else:
            logger.info("[AI Moderation] VIOLENCE проверка не вернула результат")

        logger.info(f"[AI Moderation] Сообщение {message.id} признано БЕЗОПАСНЫМ.")

    async def _handle_violation(self, message: disnake.Message, viol_type: str, reason: str, heavy: bool = False):
        user_id = message.author.id
        guild = message.guild
        
        await self.db.execute("UPDATE messages SET ai_flagged = 1, ai_reason = ? WHERE id = ?", (f"{viol_type}: {reason}", message.id))
        await self.db.commit()

        try:
            await message.delete()
        except:
            pass

        warn_embed = disnake.Embed(
            title="⚠️ Предупреждение от ИИ",
            description=f"{message.author.mention}, ты плохой молодой человек!\nТвое сообщение было удалено.\n**Причина:** {reason}",
            color=disnake.Color.orange()
        )
        try:
            await message.channel.send(embed=warn_embed, delete_after=10)
        except:
            pass
            
        bot_id = self.bot.user.id

        # Выдаём реальный тайм-аут в Discord на 1 час
        try:
            from datetime import timedelta
            await message.author.timeout(
                duration=timedelta(hours=1),
                reason=f"ИИ Автомодерация: {reason}"
            )
            logger.info(f"[AI Moderation] Мут на 1 час выдан пользователю {message.author} ({user_id})")
        except disnake.Forbidden:
            logger.error(f"[AI Moderation] Нет прав для мута пользователя {user_id}")
        except Exception as e:
            logger.error(f"[AI Moderation] Ошибка при муте пользователя {user_id}: {e}")

        # Логируем в БД: предупреждение + мут
        await self.admin_service.log_warning(user_id, bot_id, reason=f"ИИ модерация: {reason}")
        await self.admin_service.log_mute(user_id, bot_id, hours=1, minutes=0, reason=f"Автомут от ИИ: {reason}")

        # Уведомляем в канал #наказания
        await self._notify_punishments(guild, message.author, f"🔇 Мьют на 1 час. Причина: {reason}")

        if heavy:
            await self._notify_mods(guild, message.author, message.content, reason, "Тяжелое нарушение")

    async def _notify_mods(self, guild, author, content, reason, viol_type):
        log_channel = disnake.utils.get(guild.channels, name="логи")
        if log_channel:
            embed = disnake.Embed(title=f"🚨 ИИ Модерация: {viol_type}", color=disnake.Color.red())
            embed.add_field(name="Пользователь", value=author.mention)
            embed.add_field(name="Сообщение", value=content[:1024] if content else "Пусто")
            embed.add_field(name="Вердикт", value=reason)
            await log_channel.send(embed=embed)

    async def _notify_punishments(self, guild, author, reason):
        punish_channel = disnake.utils.get(guild.channels, name="наказания")
        if punish_channel:
            embed = disnake.Embed(title="🔨 Автоматическое наказание", color=disnake.Color.dark_red())
            embed.add_field(name="Пользователь", value=author.mention)
            embed.add_field(name="Наказание", value=reason)
            await punish_channel.send(embed=embed)

    @commands.slash_command(name="ai-whitelist", description="Управление whitelist каналов")
    @commands.default_member_permissions(administrator=True)
    async def ai_whitelist(self, inter: disnake.ApplicationCommandInteraction, channel: disnake.TextChannel, action: str = commands.Param(choices=["add", "remove"])):
        is_whitelisted = 1 if action == "add" else 0
        await self.db.execute(
            "INSERT INTO channel_config (channel_id, guild_id, is_ai_whitelisted) VALUES (?, ?, ?) ON CONFLICT(channel_id) DO UPDATE SET is_ai_whitelisted=?",
            (channel.id, inter.guild.id, is_whitelisted, is_whitelisted)
        )
        await self.db.commit()
        status = "добавлен в" if action == "add" else "удален из"
        await inter.response.send_message(f"Канал {channel.mention} {status} whitelist ИИ.", ephemeral=True)

    @commands.slash_command(name="ai-threshold", description="Изменить порог срабатывания ИИ")
    @commands.default_member_permissions(administrator=True)
    async def ai_threshold_cmd(self, inter: disnake.ApplicationCommandInteraction, threshold: float = commands.Param(ge=0.0, le=1.0)):
        self.ai_threshold = threshold
        await inter.response.send_message(f"Порог ИИ модерации установлен на {threshold}", ephemeral=True)

    @commands.slash_command(name="ai-review", description="Ручная проверка сообщения ИИ")
    @commands.default_member_permissions(manage_messages=True)
    async def ai_review(self, inter: disnake.ApplicationCommandInteraction, message_id: str):
        await inter.response.defer(ephemeral=True)
        try:
            msg_id_int = int(message_id)
            msg = await inter.channel.fetch_message(msg_id_int)
        except:
            await inter.edit_original_response("Сообщение не найдено.")
            return

        content = msg.content
        if not content:
            await inter.edit_original_response("Сообщение пустое.")
            return

        spam_res = await self.ai_service.classify_spam(content)
        viol_res = await self.ai_service.classify_violence(content)

        embed = disnake.Embed(title="ИИ Ревью сообщения", color=disnake.Color.blurple())
        embed.add_field(name="SPAM Check", value=f"Тип: {spam_res.get('type') if spam_res else 'None'}\nУверенность: {spam_res.get('confidence') if spam_res else 'None'}\nПричина: {spam_res.get('reason') if spam_res else 'None'}", inline=False)
        embed.add_field(name="VIOLENCE Check", value=f"Тип: {viol_res.get('type') if viol_res else 'None'}\nУверенность: {viol_res.get('confidence') if viol_res else 'None'}\nПричина: {viol_res.get('reason') if viol_res else 'None'}", inline=False)
        
        await inter.edit_original_response(embed=embed)

    @commands.slash_command(name="ai-stats-time", description="Показать статистику срабатываний ИИ за день/неделю")
    async def ai_stats_time(self, inter: disnake.ApplicationCommandInteraction):
        day_res = await self.db.fetch_one("SELECT COUNT(*) as cnt FROM messages WHERE ai_flagged = 1 AND timestamp >= datetime('now', '-1 day')")
        day_cnt = day_res['cnt'] if day_res else 0
        
        week_res = await self.db.fetch_one("SELECT COUNT(*) as cnt FROM messages WHERE ai_flagged = 1 AND timestamp >= datetime('now', '-7 days')")
        week_cnt = week_res['cnt'] if week_res else 0

        embed = disnake.Embed(title="📊 Статистика ИИ модерации", color=disnake.Color.blue())
        embed.add_field(name="Срабатываний за день", value=f"`{day_cnt}`", inline=True)
        embed.add_field(name="Срабатываний за неделю", value=f"`{week_cnt}`", inline=True)
        await inter.response.send_message(embed=embed, ephemeral=True)


def setup(bot: commands.Bot, ai_service: AIService, admin_service: AdminService, db: DatabaseManager):
    """
    Функция для загрузки cog'а
    """
    bot.add_cog(AICog(bot, ai_service, admin_service, db))
