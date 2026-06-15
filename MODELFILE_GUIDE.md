# 📚 Modelfile - Оптимизированная конфигурация Ollama

## Что это?

`Modelfile` это конфиг для создания кастомной модели Ollama с:
- ✅ Оптимизированным контекстом (2048 токенов)
- ✅ Системным промптом для Discord бота
- ✅ Поддержкой информации о пользователе (ник, роли)
- ✅ Лучшими параметрами генерации
- ✅ Поддержкой русского языка

## Как использовать?

### 1. Убедитесь что Ollama запущена
```bash
ollama serve
```

### 2. Создать кастомную модель
```bash
# В другом терминале:
ollama create my-discord-bot -f Modelfile
```

Вы должны увидеть:
```
✓ Created "my-discord-bot"
```

### 3. Обновить .env
```env
OLLAMA_ENABLED=true
OLLAMA_MODEL=my-discord-bot
```

### 4. Перезапустить бот
```bash
python main.py
```

### 5. Тестировать
```
/ai_test                    # Проверить что используется новая модель
/ai_chat Hello!             # Получить ответ от оптимизированной модели
```

## Что находится в Modelfile?

```dockerfile
FROM mistral                # Базовая модель (можно изменить на llama3, neural-chat)

SYSTEM """..."""            # Системный промпт для бота

PARAMETER temperature 0.7   # Баланс между креативностью и точностью
PARAMETER top_p 0.9        # Разнообразие ответов
PARAMETER num_ctx 2048     # Длина контекста (сокращено для скорости)
PARAMETER repeat_penalty 1.1
PARAMETER num_predict 512  # Макс длина ответа
```

## Параметры объяснены

| Параметр | Значение | Описание |
|----------|----------|---------|
| `temperature` | 0.7 | 0.0-1.0: выше = креативнее, ниже = точнее |
| `top_p` | 0.9 | Разнообразие ответов (0.0-1.0) |
| `num_ctx` | 2048 | Длина контекста в токенах (2048 = 2-3 KB текста) |
| `repeat_penalty` | 1.1 | Штраф за повтор слов |
| `num_predict` | 512 | Макс токенов в ответе |

## Модели для use

### Быстрые (для скорости)
```bash
ollama create my-bot -f Modelfile              # Основан на mistral
```
Измените в Modelfile `FROM` на:
```dockerfile
FROM neural-chat           # ⚡ Самая быстрая
FROM dolphin-mixtral      # ⚡ Быстрая
```

### Качественные (для лучших ответов)
```dockerfile
FROM llama3               # ⭐⭐⭐⭐⭐ Лучшее качество (8B)
FROM mistral             # ⭐⭐⭐⭐ Хороший баланс (7B)
FROM llama2              # ⭐⭐⭐⭐ Стабильная (7B или 13B)
```

### Маленькие (для слабого железа)
```dockerfile
FROM phi3:mini           # Очень маленькая (3.8B)
FROM neural-chat:latest # Маленькая (7B)
```

## Примеры Modelfile

### 1. Для быстрых ответов
```dockerfile
FROM neural-chat
PARAMETER temperature 0.5
PARAMETER num_ctx 1024
PARAMETER num_predict 256
```

### 2. Для творческих ответов
```dockerfile
FROM llama3
PARAMETER temperature 0.9
PARAMETER top_p 0.95
PARAMETER num_ctx 2048
PARAMETER num_predict 1024
```

### 3. Для точных и фактических ответов
```dockerfile
FROM mistral
PARAMETER temperature 0.3
PARAMETER top_p 0.7
PARAMETER repeat_penalty 1.5
```

## Отладка

### Проверить что модель создана
```bash
ollama list
```
Должна быть в списке `my-discord-bot`

### Протестировать модель напрямую
```bash
ollama run my-discord-bot "Hello, what is your purpose?"
```

### Пересоздать модель
```bash
# Удалить старую
ollama rm my-discord-bot

# Создать новую с обновленным Modelfile
ollama create my-discord-bot -f Modelfile
```

### Посмотреть свойства модели
```bash
ollama show my-discord-bot
```

## Оптимизация для вашего железа

### Если медленно
1. Уменьшить `num_ctx` (2048 → 1024)
2. Уменьшить `num_predict` (512 → 256)
3. Использовать быструю модель (neural-chat)
4. Выключить GPU в Ollama

### Если хочется красивых ответов
1. Увеличить `num_predict` (512 → 1024)
2. Увеличить `temperature` (0.7 → 0.8)
3. Использовать qualitative модель (llama3)
4. Включить GPU

## Команды для работы

```bash
# Создать
ollama create my-bot -f Modelfile

# Удалить
ollama rm my-bot

# Запустить
ollama run my-bot

# Показать информацию
ollama show my-bot

# Копировать в другую модель
ollama cp my-bot my-bot-backup
```

## Советы

💡 **Совет 1:** Скопируйте Modelfile несколько раз с разными конфигами:
```bash
cp Modelfile Modelfile.fast
cp Modelfile Modelfile.quality
```

💡 **Совет 2:** Измените базовую модель в БЫСТРЫЕ версии для скорости:
```dockerfile
FROM neural-chat        # ← Измените эту строку
```

💡 **Совет 3:** Используйте низкий `temperature` (0.3) для точных фактов:
```dockerfile
PARAMETER temperature 0.3
```

## Больше информации

- [Ollama Modelfile docs](https://github.com/ollama/ollama/blob/main/docs/modelfile.md)
- [Параметры генерации](https://github.com/ollama/ollama/blob/main/docs/modelfile.md#valid-parameters-and-values)
