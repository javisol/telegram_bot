import logging
from typing import List, Dict, Optional
from llm import conversation_context_db as db

logger = logging.getLogger(__name__)

class ConversationContextManager:
    def __init__(self, user_id: int, thread_id: str = "General", history_limit: int = 100):
        self.user_id = user_id
        self.thread_id = thread_id
        self.history_limit = history_limit
        self._history: List[Dict] = []
    
    def get_or_create(self) -> List[Dict]:
        self._history = db.get_history(self.user_id, self.thread_id, limit=self.history_limit)
        return self._history
    
    def get(self) -> List[Dict]:
        return self.get_or_create()
    
    def append(self, role: str, content: str) -> int:
        msg_id = db.append_message(self.user_id, self.thread_id, role, content)
        self._history.append({"role": role, "content": content})
        return msg_id
    
    def get_context(self, max_messages: Optional[int] = None) -> List[Dict]:
        if max_messages is None:
            max_messages = self.history_limit
        context = self.get()
        if len(context) > max_messages:
            context = context[-max_messages:]
        return context
    
    def clear(self, clear_all: bool = False) -> None:
        if clear_all:
            db.clear_user_history(self.user_id, thread_id=None)
            logger.info(f"Historial completo borrado para el usuario {self.user_id}")
        else:
            db.clear_user_history(self.user_id, self.thread_id)
            logger.info(f"Hilo '{self.thread_id}' borrado para el usuario {user_id}")
        self._history = []

