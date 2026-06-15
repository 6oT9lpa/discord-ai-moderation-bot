# 🤖 AI Moderation Module Documentation

## Overview
This module integrates **Ollama** (self-hosted LLM) with the Discord bot for AI-powered moderation and chat functionality.

## ✅ Installation & Setup

### 1. Install Ollama
- **Linux/Mac:** `curl https://ollama.ai/install.sh | sh`
- **Windows:** Download from https://ollama.ai
- **Docker:** `docker pull ollama/ollama`

### 2. Start Ollama Server
```bash
ollama serve
```

### 3. Download a Model
In another terminal:
```bash
# Recommended options:
ollama pull mistral      # Fast, good quality (7B)
ollama pull llama2       # Alternative option (7B)
ollama pull neural-chat  # Fast responses (7B)
```

### 4. Configure Environment
Edit your `.env` file:
```env
OLLAMA_ENABLED=true
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=mistral
```

## 📝 Discord Commands

### Chat Commands
#### `/ai_chat <message>`
Communicate with the AI assistant. Maintains conversation history per user.
```
/ai_chat How do I setup roles?
```
- Max message length: 1000 characters
- Responses limited to 2000 characters (Discord limit)
- Conversation history saved automatically

#### `/ai_clear`
Clear your conversation history with the AI.
```
/ai_clear
```

#### `/ai_history`
View last 10 messages from your conversation.
```
/ai_history
```

### Admin Commands
#### `/ai_stats`
Show moderation statistics (counts of flagged messages).
```
/ai_stats
```

#### `/ai_test`
Test connection to Ollama and display model info.
```
/ai_test
```
Output will show:
- ✅ Connection status
- Model name
- Ollama URL
- Installation instructions if not connected

## 🚀 Features

### Chat with AI
- **Persistent History:** Each user has their own conversation history
- **Context Aware:** AI remembers previous messages in the conversation
- **System Prompts:** Customizable behavior for different use cases
- **Timeout:** 30-second timeout for responses

### Moderation Classification (Backend)
Three classification types available for future moderation features:

1. **Spam Detection** (`classify_spam`)
   - Detects spam and advertising
   - Returns: `SPAM` | `SAFE`
   - Confidence score (0.0-1.0)

2. **Violence & Bullying** (`classify_violence`)
   - Detects violence, bullying, NSFW
   - Returns: `VIOLENCE` | `BULLYING` | `NSFW` | `SAFE`

3. **Safety Threats** (`classify_safety`)
   - Detects dangerous links, phishing
   - Returns: `DANGEROUS` | `SAFE`

## 🔧 Technical Details

### Project Structure
```
infrastructure/
├── ai/
│   └── ollama_client.py          # Ollama HTTP client
├── config/
│   └── settings.py               # AI configuration
│   
application/
├── services/
│   └── ai_service.py             # AI business logic
│   
presentation/
├── cogs/
│   └── ai_cog.py                 # Discord commands
│   
di/
├── container.py                  # Dependency injection
├── bootstrap.py                  # Service initialization
```

### Configuration (BotConfig)
```python
ollama_base_url: str = "http://localhost:11434"
ollama_model: str = "mistral"
ollama_enabled: bool = False
```

### Services

#### OllamaClient
```python
client = OllamaClient(base_url, model)
await client.init_session()
response = await client.generate(prompt, system_prompt)
result = await client.classify(text, classification_type)
await client.close_session()
```

#### AIService
```python
service = AIService(ollama_client)
response = await service.chat(user_id, message)
await service.classify_spam(text)
await service.classify_violence(text)
stats = service.get_stats()
```

## ⚠️ Performance Notes

### Latency
- **Cold start:** 3-10 seconds (first inference)
- **Subsequent requests:** 1-5 seconds (depends on model and hardware)
- **Timeout configured:** 30 seconds

### Model Recommendations by Performance
| Model | Speed | Quality | Size | VRAM |
|-------|-------|---------|------|------|
| neural-chat | ⚡⚡⚡ | ⭐⭐⭐ | 7B | 4GB |
| mistral | ⚡⚡ | ⭐⭐⭐⭐ | 7B | 4GB |
| llama2 | ⚡⚡ | ⭐⭐⭐⭐ | 7B | 4GB |
| openchat | ⚡⚡⭐ | ⭐⭐⭐⭐ | 7B | 4GB |

### Hardware Requirements
- **Minimum:** 4GB RAM (CPU mode is slow)
- **Recommended:** GPU with VRAM for acceleration
  - NVIDIA: CUDA compatible GPU
  - AMD: ROCm support
  - Mac: Native Metal acceleration

## 🐛 Troubleshooting

### Connection Errors
```
✗ Ollama connection timeout
```
**Solution:**
1. Ensure Ollama is running: `ollama serve`
2. Check URL in `.env`: `OLLAMA_BASE_URL=http://localhost:11434`
3. Test connection: `/ai_test` command

### No Response from AI
1. Check Ollama is still running
2. Verify model is downloaded: `ollama list`
3. Check bot logs for timeout errors

### Responses Too Slow
1. Use faster model: `neural-chat` instead of `mistral`
2. Enable GPU acceleration in Ollama
3. Reduce concurrent requests (rate limit)

### Memory Issues
1. Reduce model size (7B vs 13B)
2. Check system RAM availability
3. Consider running Ollama on separate machine

## 🔜 Future Enhancements
- [ ] Auto-moderation on message create
- [ ] Whitelist channels exempt from checking
- [ ] Adjustable confidence thresholds
- [ ] Auto-mute/warn on violations
- [ ] Message logging to database
- [ ] Web dashboard for stats
- [ ] Multi-language support
- [ ] Fine-tuned safety prompts

## 📚 Related Files
- [Ollama Documentation](https://ollama.ai)
- [OllamaClient API](./infrastructure/ai/ollama_client.py)
- [AIService API](./application/services/ai_service.py)
- [Environment Config](./.env.example)

## 💡 Tips
- Start with `neural-chat` model for fastest responses
- Use system prompts to customize AI behavior
- Monitor `/ai_stats` to track moderation activity
- Run `/ai_test` regularly to verify connection
