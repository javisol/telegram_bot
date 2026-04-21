"""
Conversation Context Manager for multi-turn LLM conversations.

This module provides a high-level interface for managing per-user
conversation history, including getting, appending, and retrieving
conversation context for LLM API calls.
"""
import os
import logging
from typing import List, Dict, Optional

from conversation_context_db import (
    get_history,
    append_message,
    get_or_create_history,
    save_history,
    get_message_count,
    get_last_message,
    cleanup_old_messages
)

logger = logging.getLogger(__name__)

# Default configuration
DEFAULT_HISTORY_LIMIT = 20  # Number of messages to pass to LLM
DEFAULT_HISTORY_TTL_DAYS = 7  # Days to keep history (for cleanup)


class ConversationContextManager:
    """
    Manages conversation context for multi-turn LLM interactions.
    
    This class handles storing and retrieving conversation history per user,
    preparing context for LLM API calls, and managing history lifecycle.
    
    Attributes:
        user_id: The user ID for this conversation context
        history_limit: Maximum number of messages to keep in context
    """
    
    def __init__(self, user_id: int, history_limit: int = DEFAULT_HISTORY_LIMIT):
        """
        Initialize the conversation context manager.
        
        Args:
            user_id: Telegram user ID
            history_limit: Maximum messages to keep in context (default: 20)
        """
        self.user_id = user_id
        self.history_limit = history_limit
        self._history: List[Dict] = []
    
    def get_or_create(self) -> List[Dict]:
        """
        Get existing conversation history or create a new one.
        
        Returns:
            List[Dict]: Current conversation history
        """
        self._history = get_or_create_history(self.user_id)
        logger.info(f"Got/created conversation for user {self.user_id}, "
                    f"current size: {len(self._history)}")
        return self._history
    
    def get(self) -> List[Dict]:
        """
        Get current conversation history.
        
        Returns:
            List[Dict]: Current conversation history
        """
        if not self._history:
            self.get_or_create()
        return self._history
    
    def append(self, role: str, content: str) -> int:
        """
        Append a message to the conversation history.
        
        Args:
            role: Message role ('system', 'user', 'assistant')
            content: Message content
        
        Returns:
            int: The ID of the inserted message
        """
        message_id = append_message(self.user_id, role, content)
        self._history.append({
            "role": role,
            "content": content
        })
        logger.info(f"Appended message for user {self.user_id}, "
                    f"new size: {len(self._history)}")
        return message_id
    
    def get_context(self, max_messages: int = None) -> List[Dict]:
        """
        Get conversation context for LLM API call.
        
        Args:
            max_messages: Maximum messages to include (default: history_limit)
        
        Returns:
            List[Dict]: Conversation context messages
        """
        if max_messages is None:
            max_messages = self.history_limit
        
        context = self.get()
        # Limit to most recent messages
        if len(context) > max_messages:
            context = context[-max_messages:]
        
        logger.debug(f"Got context for user {self.user_id}, "
                     f"messages: {len(context)} (limit: {max_messages})")
        return context
    
    def save(self, messages: List[Dict]) -> None:
        """
        Save a complete conversation history.
        
        Args:
            messages: List of message dictionaries
        """
        save_history(self.user_id, messages)
        self._history = messages
        logger.info(f"Saved conversation for user {self.user_id}, "
                    f"size: {len(messages)}")
    
    def get_message_count(self) -> int:
        """
        Get total message count in conversation.
        
        Returns:
            int: Total message count
        """
        return get_message_count(self.user_id)
    
    def get_last_message(self) -> Optional[Dict]:
        """
        Get the most recent message.
        
        Returns:
            Optional[Dict]: Last message or None if no history
        """
        return get_last_message(self.user_id)
    
    def cleanup_old(self, keep_recent: int = None) -> int:
        """
        Remove old messages, keeping only the most recent ones.
        
        Args:
            keep_recent: Number of recent messages to keep (default: history_limit)
        
        Returns:
            int: Number of messages deleted
        """
        if keep_recent is None:
            keep_recent = self.history_limit
        
        deleted = cleanup_old_messages(self.user_id, keep_recent)
        self._history = self.get()[:keep_recent]
        return deleted
    
    def clear(self) -> None:
        """
        Clear the conversation history.
        """
        # Remove from database
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM conversation_history WHERE user_id = ?", 
                       (self.user_id,))
        conn.commit()
        conn.close()
        
        self._history = []
        logger.info(f"Cleared conversation for user {self.user_id}")
    
    def __len__(self) -> int:
        """
        Get current conversation size.
        
        Returns:
            int: Number of messages in current context
        """
        if not self._history:
            self.get_or_create()
        return len(self._history)


# Singleton database connection for efficiency
def get_connection() -> sqlite3.Connection:
    """
    Get a database connection, creating the database and tables if needed.
    
    Returns:
        sqlite3.Connection: Database connection
    """
    import sqlite3
    from conversation_context_db import DB_PATH
    
    # Ensure data directory exists
    db_dir = os.path.dirname(DB_PATH)
    if db_dir and not os.path.exists(db_dir):
        os.makedirs(db_dir)
        logger.info(f"Created data directory: {db_dir}")
    
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    from conversation_context_db import init_tables
    init_tables(conn)
    return conn
