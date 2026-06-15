from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from infrastructure.ai.ollama_client import OllamaClient
from infrastructure.logging import get_logger

logger = get_logger(__name__)


class AIService:
    """
    Сервис для управления ИИ модерацией и взаимодействия с Ollama
    """
    
    def __init__(self, ollama_client: OllamaClient):
        self._ollama = ollama_client
        self._conversation_history: Dict[int, list] = {}  # user_id -> список сообщений
        self._moderation_stats = {
            "spam_detected": 0,
            "violence_detected": 0,
            "safety_detected": 0,
            "last_reset": datetime.now()
        }
        logger.info("AIService initialized")
    
    async def chat(
        self,
        user_id: int,
        message: str,
        system_prompt: Optional[str] = None,
        user_info: Optional[Dict[str, Any]] = None,
        use_history: bool = True
    ) -> Optional[str]:
        """
        Общая функция чата с ИИ
        
        Args:
            user_id: ID пользователя в Discord
            message: Сообщение от пользователя
            system_prompt: Системный промпт (если None, используется стандартный)
            user_info: Информация о пользователе (ник, роли, ID)
            use_history: Использовать ли историю сообщений
            
        Returns:
            Ответ от ИИ или None при ошибке
        """
        if system_prompt is None:
            system_prompt = """Ты помощник на Discord сервере. 
Ты вежлив, полезен и уважителен. 
Отвечай кратко и по сути (максимум 2000 символов для Discord).
Используй русский язык.
Если вопрос выходит за рамки компетенции, предложи обратиться к администратору."""
        
        # Формировать информацию о пользователе для контекста
        user_context = ""
        if user_info:
            username = user_info.get("username", "Unknown")
            roles = user_info.get("roles", [])
            is_admin = user_info.get("is_admin", False)
            roles_str = ", ".join(roles) if roles else "нет ролей"
            admin_status = "admin" if is_admin else "user"
            
            user_context = f"\n[ник: {username} | роли: {roles_str} | статус: {admin_status}]"
        
        # Инициализировать историю если её нет
        if user_id not in self._conversation_history and use_history:
            self._conversation_history[user_id] = []
        
        # Добавить сообщение пользователя в историю
        if use_history:
            self._conversation_history[user_id].append({
                "role": "user",
                "content": message
            })
            # Ограничить историю последними 10 сообщениями
            if len(self._conversation_history[user_id]) > 20:
                self._conversation_history[user_id] = self._conversation_history[user_id][-20:]
        
        # Формировать полный промпт с информацией о пользователе
        if use_history and self._conversation_history[user_id]:
            full_prompt = f"{user_context}\n{message}"
        else:
            full_prompt = f"{user_context}\n{message}"
        
        response = await self._ollama.generate(
            prompt=full_prompt,
            system_prompt=system_prompt,
            temperature=0.7,
            timeout=180,
            num_predict=300
        )
        
        if response and use_history:
            self._conversation_history[user_id].append({
                "role": "assistant",
                "content": response
            })
        
        return response
    
    async def classify_spam(self, text: str) -> Optional[Dict[str, Any]]:
        """Классифицировать текст как спам или нет"""
        result = await self._ollama.classify(text, "spam")
        if result:
            self._moderation_stats["spam_detected"] += 1
        return result
    
    async def classify_violence(self, text: str) -> Optional[Dict[str, Any]]:
        """Классифицировать текст на насилие и буллинг"""
        result = await self._ollama.classify(text, "violence")
        if result and result.get("type") != "SAFE":
            self._moderation_stats["violence_detected"] += 1
        return result
    
    async def classify_safety(self, text: str) -> Optional[Dict[str, Any]]:
        """Классифицировать текст на опасный контент"""
        result = await self._ollama.classify(text, "safety")
        if result and result.get("type") != "SAFE":
            self._moderation_stats["safety_detected"] += 1
        return result
    
    def clear_conversation(self, user_id: int):
        """Очистить историю беседы пользователя"""
        if user_id in self._conversation_history:
            del self._conversation_history[user_id]
            logger.info(f"Conversation history cleared for user {user_id}")
    
    def get_conversation_history(self, user_id: int) -> list:
        """Получить историю беседы пользователя"""
        return self._conversation_history.get(user_id, [])
    
    def get_stats(self) -> Dict[str, Any]:
        """Получить статистику модерации"""
        return {
            "spam_detected": self._moderation_stats["spam_detected"],
            "violence_detected": self._moderation_stats["violence_detected"],
            "safety_detected": self._moderation_stats["safety_detected"],
            "last_reset": self._moderation_stats["last_reset"].isoformat()
        }
    
    def reset_stats(self):
        """Очистить статистику"""
        self._moderation_stats = {
            "spam_detected": 0,
            "violence_detected": 0,
            "safety_detected": 0,
            "last_reset": datetime.now()
        }
        logger.info("Moderation stats reset")
