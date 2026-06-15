# 🚀 Quick Start - AI Module

## ✨ Что нового?

- ✅ **AI видит вас!** Знает ваш ник и роли
- ✅ **Урезанный контекст** - быстрые ответы (2-5 сек)
- ✅ **Modelfile оптимизация** - лучшие параметры
- ✅ **Команда /ai_chat** - общайтесь с нейросетью

## 1️⃣ Start Ollama (One-time setup)

### Download & Install
- Visit https://ollama.ai
- Download for your OS
- Install it

### Run Ollama Server
```bash
ollama serve
```

### Download Model (in another terminal)
```bash
ollama pull mistral
```

## 2️⃣ Configure Bot

Edit `.env` file:
```env
OLLAMA_ENABLED=true
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=mistral
```

## 3️⃣ Start Bot
```bash
python main.py
```

## 4️⃣ Use Commands in Discord

### Chat with AI
```
/ai_chat Tell me about Discord roles
```
AI видит: `[ник: YourName | роли: admin, moderator | статус: admin]`

### View Conversation
```
/ai_history
```

### Clear History
```
/ai_clear
```

### Check Stats
```
/ai_stats
```

### Test Connection
```
/ai_test
```

## 🔧 Custom Modelfile (Optional)

We provide an optimized `Modelfile`:

```bash
# Build custom model
ollama create my-bot -f Modelfile

# Then use in .env:
OLLAMA_MODEL=my-bot
```

The Modelfile includes:
- Optimized context window (2048 tokens)
- Russian language support
- User role awareness
- Performance optimizations

## ⚡ Performance Tips
- **Fast responses:** Use `neural-chat` model
- **Better quality:** Use `mistral` or `llama3`
- **GPU:** Much faster with NVIDIA/AMD GPU

## 🆘 Not Working?
1. Run `/ai_test` - shows connection status
2. Check Ollama is running: `ollama serve` terminal
3. Verify `.env` has `OLLAMA_ENABLED=true`
4. Check model exists: `ollama list`

---

Full documentation: [AI_MODERATION_README.md](./AI_MODERATION_README.md)
