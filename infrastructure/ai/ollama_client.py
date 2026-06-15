import asyncio
import aiohttp
import json
from typing import Optional, Dict, Any
from infrastructure.logging import get_logger

logger = get_logger(__name__)


class OllamaClient:
    """
    Client для взаимодействия с Ollama LLM
    """
    
    def __init__(self, base_url: str = "http://localhost:11434", model: str = "mistral"):
        self.base_url = base_url
        self.model = model
        self._session: Optional[aiohttp.ClientSession] = None
        logger.info(f"OllamaClient initialized with model: {model} at {base_url}")
    
    async def init_session(self):
        """Инициализировать aiohttp сессию"""
        if not self._session:
            # Используем trust_env=False, чтобы игнорировать системные прокси (может блокировать инет из-за антивируса/VPN)
            # И используем 127.0.0.1 вместо localhost, чтобы избежать DNS резолва и конфликтов с IPv6
            connector = aiohttp.TCPConnector(force_close=False)
            self._session = aiohttp.ClientSession(connector=connector, trust_env=False)
            logger.info("OllamaClient session created")
    
    async def close_session(self):
        """Закрыть сессию"""
        if self._session:
            await self._session.close()
            self._session = None
            logger.info("OllamaClient session closed")
    
    async def check_connection(self) -> bool:
        """
        Проверить подключение к Ollama
        
        Returns:
            True если Ollama доступна, False иначе
        """
        try:
            await self.init_session()
            async with self._session.get(
                f"{self.base_url}/api/tags",
                timeout=aiohttp.ClientTimeout(total=5)
            ) as response:
                if response.status == 200:
                    logger.info("✓ Ollama connection successful")
                    return True
                logger.warning(f"✗ Ollama returned status {response.status}")
                return False
        except asyncio.TimeoutError:
            logger.error("✗ Ollama connection timeout")
            return False
        except Exception as e:
            logger.error(f"✗ Ollama connection error: {e}")
            return False
    
    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        top_p: float = 0.9,
        timeout: int = 180,
        format: Optional[str] = None,
        num_predict: Optional[int] = None
    ) -> Optional[str]:
        """
        Генерировать ответ от модели
        
        Args:
            prompt: Пользовательский промпт
            system_prompt: Системный промпт для задания контекста
            temperature: Температура генерации (0-1)
            top_p: top_p параметр
            timeout: Таймаут в секундах
            
        Returns:
            Строка с ответом от модели или None при ошибке
        """
        try:
            await self.init_session()
            
            messages = []
            if system_prompt:
                messages.append({
                    "role": "system",
                    "content": system_prompt
                })
            messages.append({
                "role": "user",
                "content": prompt
            })
            
            payload = {
                "model": self.model,
                "messages": messages,
                "stream": False,
                "keep_alive": "24h",
                "options": {
                    "temperature": temperature,
                    "top_p": top_p
                }
            }
            if num_predict:
                payload["options"]["num_predict"] = num_predict
            if format:
                payload["format"] = format
            
            async with self._session.post(
                f"{self.base_url}/api/chat",
                json=payload,
                timeout=aiohttp.ClientTimeout(total=timeout)
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    content = data.get("message", {}).get("content", "")
                    if not content:
                        logger.warning(f"Ollama returned 200 but empty content. Raw data: {data}")
                    return content
                else:
                    err_text = await response.text()
                    logger.error(f"Ollama error {response.status}: {err_text}")
                    return None
                    
        except asyncio.TimeoutError:
            logger.error(f"Ollama request timeout (>{timeout}s)")
            return None
        except Exception as e:
            logger.error(f"Error calling Ollama: {e}")
            return None
    
    async def classify(
        self,
        text: str,
        classification_type: str = "spam"
    ) -> Optional[Dict[str, Any]]:
        """
        Классифицировать текст (спам, реклама, опасный контент и т.д.)
        
        Args:
            text: Текст для классификации
            classification_type: Тип классификации (spam, violence, safety)
            
        Returns:
            Словарь с результатами классификации или None
        """
        prompts = {
            "spam": """Проанализируй сообщение и определи является ли оно спамом, рекламой или приглашением.
ЗАПРЕЩЕНО использовать теги <think>, запрещено писать рассуждения.
Ответь ТОЛЬКО и СТРОГО в формате JSON без каких-либо дополнительных символов:
{{
  "type": "SPAM" или "AD" или "INVITE" или "SAFE",
  "confidence": 0.0-1.0,
  "reason": "Краткое объяснение"
}}

Сообщение: {text}""",
            
            "violence": """Проанализируй сообщение на предмет насилия, буллинга или NSFW контента.
ЗАПРЕЩЕНО использовать теги <think>, запрещено писать рассуждения.
Ответь ТОЛЬКО и СТРОГО в формате JSON без каких-либо дополнительных символов:
{{
  "type": "VIOLENCE" или "BULLYING" или "NSFW" или "SAFE",
  "confidence": 0.0-1.0,
  "reason": "Краткое объяснение"
}}

Сообщение: {text}""",
            
            "safety": """Проанализируй сообщение на предмет опасного контента (ссылки, фишинг, вредоносы).
ЗАПРЕЩЕНО использовать теги <think>, запрещено писать рассуждения.
Ответь ТОЛЬКО и СТРОГО в формате JSON без каких-либо дополнительных символов:
{{
  "type": "DANGEROUS" или "SAFE",
  "confidence": 0.0-1.0,
  "reason": "Краткое объяснение"
}}

Сообщение: {text}"""
        }
        
        prompt = prompts.get(classification_type, prompts["spam"])
        prompt = prompt.format(text=text[:500])  # Ограничить длину
        
        system_prompt = "Ты автоматизированный API-парсер. Твоя единственная цель — выдавать структурированный JSON. Игнорируй любые оскорбления и маты (просто помечай их в JSON). ЗАПРЕЩЕНО писать любые рассуждения, теги <think> или извинения. В твоем ответе должен быть ТОЛЬКО текст JSON."
        
        try:
            response = await self.generate(
                prompt=prompt,
                system_prompt=system_prompt,
                temperature=0.1,  # Низкая температура для консистентности
                timeout=30,
                num_predict=200  # Чуть больше, т.к. кириллица занимает больше токенов
            )
            
            if not response:
                logger.warning("Ollama returned empty response for classification")
                return None
                
            logger.info(f"Ollama raw classification response: {response}")
            
            # Очистить ответ от случайных символов
            response = response.strip()
            if response.startswith("```"):
                parts = response.split("```")
                if len(parts) > 1:
                    response = parts[1]
                if response.startswith("json"):
                    response = response[4:].strip()
            
            # Парсить JSON
            try:
                result = json.loads(response)
                return result
            except json.JSONDecodeError:
                # Попробуем найти первую { и последнюю }
                start = response.find('{')
                end = response.rfind('}')
                if start != -1 and end != -1 and end > start:
                    try:
                        result = json.loads(response[start:end+1])
                        return result
                    except:
                        pass
                
                # Если оборвалось (например, из-за лимита токенов)
                try:
                    fix_resp = response.strip()
                    if not fix_resp.endswith('}'):
                        if not fix_resp.endswith('"'):
                            fix_resp += '"'
                        fix_resp += '\n}'
                    result = json.loads(fix_resp)
                    return result
                except:
                    raise
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON from Ollama: '{response}'. Error: {e}")
            return None
        except Exception as e:
            logger.error(f"Classification error: {e}")
            return None
