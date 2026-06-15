# 🤖 Discord AI Moderation Bot

<div align="center">

**Discord бот с AI модерацией на Ollama (self-hosted LLM). Автовыдача ролей, мониторинг стримов Twitch/YouTube/Kick, динамические голосовые каналы, статистика сервера, логирование в SQLite, панель администратора, Dev Blog. Чистая архитектура, DI контейнер, systemd деплой. Python 3.12 + disnake.**

[![Python](https://img.shields.io/badge/Python-3.12-blue.svg)](https://python.org)
[![disnake](https://img.shields.io/badge/disnake-2.9.2-green.svg)](https://github.com/DisnakeDev/disnake)
[![Ollama](https://img.shields.io/badge/Ollama-AI-orange.svg)](https://ollama.ai)
[![SQLite](https://img.shields.io/badge/SQLite-Database-blue.svg)](https://sqlite.org)
[![License](https://img.shields.io/badge/License-MIT-red.svg)](LICENSE)

</div>

---

## 📋 О проекте

Этот бот создан для полной автоматизации управления Discord сервером. **Ключевая особенность** — self-hosted AI модерация через Ollama, что означает полный контроль над данными без отправки сообщений во внешние API.

### 🎯 Основные возможности

| Модуль                   | Описание                                                                  |
| ------------------------ | ------------------------------------------------------------------------- |
| 🧠 **AI Модерация**      | Локальная LLM (Mistral/Llama3/Phi3) для детекции спама, рекламы, буллинга |
| 🎮 **Стрим-мониторинг**  | Twitch, YouTube, Kick — авто-анонсы при старте стрима                     |
| 👥 **Роли**              | Автовыдача, интерактивные панели с кнопками                               |
| 🔊 **Голосовые комнаты** | Динамическое создание, управление владельцем                              |
| 📊 **Статистика**        | Топ активности, графики, счётчики в реальном времени                      |
| 🛠️ **Админ-панель**     | Варны, муты, баны, очистка чата                                           |
| 📝 **Логирование**       | Полный аудит сообщений и действий в SQLite                                |
| 📰 **Dev Blog**          | Публикация постов с тегами и комментариями                                |

---

## 🚀 Быстрый старт

### Требования

| Компонент          | Минимум | Рекомендуется |
| ------------------ | ------- | ------------- |
| Python             | 3.12    | 3.12+         |
| RAM (без AI)       | 2GB     | 4GB           |
| RAM (с AI Mistral) | 8GB     | 16GB          |
| Диск               | 10GB    | 20GB          |
| ОС                 | Linux   | Ubuntu 22.04+ |

### Установка за 5 минут

```bash
git clone https://github.com/6oT9lpa/discord-ai-moderation-bot.git
cd discord-ai-moderation-bot

python3.12 -m venv venv
source venv/bin/activate

pip install -r requirements.txt

cp .env.example .env
nano .env

python main.py
```

### Установка Ollama

```bash
curl -fsSL https://ollama.com/install.sh | sh

ollama pull mistral
# или
ollama pull llama3
# или
ollama pull phi3:mini

ollama list

curl http://localhost:11434/api/generate \
-d '{"model":"mistral","prompt":"Hello"}'
```

### Docker

```bash
docker-compose up -d
```

---

# 📦 Модули

## 🤖 AI Модерация

**Локальная LLM без отправки данных во внешние API!**

### Команды
```bash
/ai_chat <сообщение>    # Общайтесь с ИИ
/ai_clear              # Очистить историю
/ai_history            # Показать последние 10 сообщений
/ai_stats              # Статистика модерации
/ai_test               # Проверить подключение к Ollama
```

### Особенности
- ✅ **Персональная история** - ИИ помнит контекст беседы
- ✅ **Знание о пользователе** - ИИ видит ник и роли
- ✅ **Быстрые ответы** - 2-5 сек благодаря оптимизированному контексту
- ✅ **Классификация** - Спам, насилие, буллинг, NSFW
- ✅ **Локально** - Никакие данные не отправляются в облако

### Модели Ollama
| Модель | Скорость | Качество | Рекомендуется |
|--------|----------|----------|--------------|
| neural-chat | ⚡⚡⚡ | ⭐⭐ | Для скорости |
| mistral | ⚡⚡ | ⭐⭐⭐ | Баланс |
| llama3 | ⚡ | ⭐⭐⭐⭐⭐ | Лучшее качество |

### Установка

1. **Установить Ollama**
```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

2. **Скачать модель**
```bash
ollama serve &
ollama pull mistral
```

3. **Включить в .env**
```env
OLLAMA_ENABLED=true
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=mistral
```

4. **Создать custom Modelfile (опционально)**
```bash
ollama create my-custom-model -f Modelfile
```

### Пример использования
```
👤 User: /ai_chat Как установить роли?
🤖 Bot: Для установки ролей используйте команду /role-panel setup...
        (помнит что вы admin с роли "Администратор")

👤 User: /ai_chat А как это сделать для модераторов?
🤖 Bot: (использует контекст из предыдущего сообщения)
```

---

## 🛡️ Роли и автовыдача

```bash
/role-panel setup #роли
/role-panel add @Геймер
/role-autoassign set @Участник
/roles-list
```

---

## 📺 Стримы и публикации

```bash
/streamer add twitch https://twitch.tv/nick
/stream-template set
/subscribe youtube UCxxxxx
```

Поддерживаются:

* Twitch
* YouTube
* Kick

---

## 🔊 Голосовые каналы

```bash
/room name "Моя комната"
/room limit 5
/room lock
/room transfer @user
```

---

## 📊 Статистика

```bash
/stats server
/stats user @user
/leaderboard
```

---

## 🛠️ Администрирование

```bash
/warn @user причина
/mute @user 10m причина
/kick @user причина
/ban @user причина
/purge 50
/slowmode #chat 5
```

---

## 📝 Логирование

Сохраняются:

* сообщения
* удаления сообщений
* изменения сообщений
* вход/выход участников
* наказания
* изменения ролей

База данных: SQLite

---

## 📰 Dev Blog

```bash
/blog post
/blog list --tag dev
/blog archive
```

---

# ⚙️ Конфигурация

## .env

```env
TOKEN=your_discord_bot_token_here
GUILD_ID=123456789012345678
OWNER_ID=987654321098765432

OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=mistral

TWITCH_CLIENT_ID=your_twitch_id
TWITCH_CLIENT_SECRET=your_twitch_secret

YOUTUBE_API_KEY=your_youtube_key
```

### Настройка через Discord

```bash
/bot config view
/bot config set KEY value
/bot reload cog
/bot status
```

---

# 🐳 Docker Compose

```yaml
version: '3.8'

services:
  bot:
    build: .
    container_name: discord-bot
    restart: unless-stopped
    env_file:
      - .env
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
    depends_on:
      - ollama

  ollama:
    image: ollama/ollama:latest
    container_name: ollama
    restart: unless-stopped
    volumes:
      - ./ollama_models:/root/.ollama
    ports:
      - "11434:11434"
```

---

# 🔧 Деплой на VPS

## Systemd сервис

```ini
[Unit]
Description=Discord AI Moderation Bot
After=network.target ollama.service

[Service]
Type=simple
User=discord
WorkingDirectory=/opt/discord-bot
EnvironmentFile=/opt/discord-bot/.env
ExecStart=/opt/discord-bot/venv/bin/python main.py
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
```

### Управление

```bash
sudo systemctl enable discord-bot
sudo systemctl start discord-bot
sudo systemctl status discord-bot
```

---

## Ежедневные бэкапы

```cron
0 3 * * * sqlite3 /opt/discord-bot/data/bot.db ".backup '/opt/discord-bot/backups/bot_$(date +\%Y\%m\%d).db'"
```

---

# 🏗️ Архитектура

```text
discord-ai-moderation-bot/
├── core/
├── application/
├── infrastructure/
├── presentation/
├── di/
├── tests/
├── main.py
└── requirements.txt
```

### Используемые подходы

* Clean Architecture
* Dependency Injection
* Repository Pattern
* Service Layer
* SQLite Persistence

---

# 📊 Мониторинг

| Команда                        | Назначение           |
| ------------------------------ | -------------------- |
| `/bot uptime`                  | Время работы         |
| `/bot ping`                    | Задержка Discord API |
| `/ai-stats`                    | Статистика AI        |
| `journalctl -u discord-bot -f` | Просмотр логов       |

---

# ❓ FAQ

### Бот не видит сообщения

Включите в Discord Developer Portal:

* MESSAGE CONTENT INTENT
* SERVER MEMBERS INTENT

### AI не работает

```bash
systemctl status ollama
ollama pull mistral

curl http://localhost:11434/api/generate \
-d '{"model":"mistral","prompt":"Hi"}'
```

### Бот не выдаёт роли

Роль бота должна находиться выше выдаваемых ролей.

### database is locked

```sql
PRAGMA journal_mode=WAL;
```

---

# 🧪 Тестирование

```bash
pytest tests/unit -v

pytest --cov=. --cov-report=html

pytest tests/unit/test_ai_moderation.py -v
```

---

# 📄 Лицензия

MIT License

Copyright (c) 2025-2026 6oT9lpa

---

# 🌟 Поддержка

* GitHub Issues
* Pull Requests
* Discussions

Автор: **6oT9lpa**

<div align="center">

⭐ Если проект оказался полезным, поставьте звезду репозиторию ⭐

Built with ❤️ for Discord Communities

</div>
