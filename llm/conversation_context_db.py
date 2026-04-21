"""
SQLite database operations for conversation context storage.

This module handles all database interactions for storing and retrieving
conversation history per user.
"""
import os
import sqlite3
import logging
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)

# Database path - store in project directory
DB_PATH = os.environ.get("LLM_CONVERSATION_DB_PATH", "data/llm_conversation.db")


def get_connection() -> sqlite3.Connection:
    """
    Get a database connection, creating the database and tables if needed.
    
    Returns:
        sqlite3.Connection: Database connection
    """
    # Ensure data directory exists
    db_dir = os.path.dirname(DB_PATH)
    if db_dir and not os.path.exists(db_dir):
        os.makedirs(db_dir)
        logger.info(f"Created data directory: {db_dir}")
    
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Enable dict-like access
    init_tables(conn)
    return conn


def init_tables(conn: sqlite3.Connection) -> None:
    """
    Initialize database tables if they don't exist.
    
    Args:
        conn: Database connection
    """
    cursor = conn.cursor()
    
    # Create conversation_history table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS conversation_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            message_index INTEGER DEFAULT 0
        )
    """)
    
    # Create indexes for performance
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_user_id ON conversation_history(user_id)
    """)
    
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_timestamp ON conversation_history(timestamp)
    """)
    
    conn.commit()
    logger.info("Database tables initialized")


def get_history(user_id: int, limit: int = 20) -> List[Dict]:
    """
    Get conversation history for a user, limited to the most recent messages.
    
    Args:
        user_id: User ID
        limit: Maximum number of messages to return (default: 20)
    
    Returns:
        List[Dict]: List of message dictionaries with role and content
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT role, content, timestamp
        FROM conversation_history
        WHERE user_id = ?
        ORDER BY timestamp DESC
        LIMIT ?
    """, (user_id, limit))
    
    rows = cursor.fetchall()
    messages = [
        {
            "role": row["role"],
            "content": row["content"],
            "timestamp": row["timestamp"]
        }
        for row in rows
    ]
    
    # Reverse to get chronological order
    messages.reverse()
    
    conn.close()
    return messages


def append_message(user_id: int, role: str, content: str) -> int:
    """
    Append a message to the user's conversation history.
    
    Args:
        user_id: User ID
        role: Message role ('system', 'user', 'assistant')
        content: Message content
    
    Returns:
        int: The ID of the inserted message
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO conversation_history (user_id, role, content, message_index)
        VALUES (?, ?, ?, 0)
    """, (user_id, role, content))
    
    message_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    logger.info(f"Appended message (ID={message_id}) for user {user_id}")
    return message_id


def get_or_create_history(user_id: int) -> List[Dict]:
    """
    Get existing history or create a new empty conversation for the user.
    
    Args:
        user_id: User ID
    
    Returns:
        List[Dict]: Current conversation history (empty list if new user)
    """
    history = get_history(user_id, limit=100)  # Get all for potential reordering
    
    # Check if user has any history
    if not history:
        logger.info(f"New user {user_id}, initializing empty conversation")
        # Create a new entry to mark the user exists
        append_message(user_id, "system", "Conversation initialized")
        return get_history(user_id, limit=20)
    
    return history


def save_history(user_id: int, messages: List[Dict]) -> None:
    """
    Save a complete conversation history for a user.
    
    Args:
        user_id: User ID
        messages: List of message dictionaries
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    # Clear existing history for this user
    cursor.execute("DELETE FROM conversation_history WHERE user_id = ?", (user_id,))
    
    # Insert new messages
    for msg in messages:
        cursor.execute("""
            INSERT INTO conversation_history (user_id, role, content, message_index)
            VALUES (?, ?, ?, 0)
        """, (user_id, msg["role"], msg["content"]))
    
    conn.commit()
    conn.close()
    logger.info(f"Saved conversation history for user {user_id}")


def get_message_count(user_id: int) -> int:
    """
    Get the total number of messages in a user's conversation.
    
    Args:
        user_id: User ID
    
    Returns:
        int: Total message count
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT COUNT(*) FROM conversation_history
        WHERE user_id = ?
    """, (user_id,))
    
    count = cursor.fetchone()[0]
    conn.close()
    return count


def get_last_message(user_id: int) -> Optional[Dict]:
    """
    Get the most recent message from a user's conversation.
    
    Args:
        user_id: User ID
    
    Returns:
        Optional[Dict]: Last message or None if no history
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT role, content, timestamp
        FROM conversation_history
        WHERE user_id = ?
        ORDER BY timestamp DESC
        LIMIT 1
    """, (user_id,))
    
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return {
            "role": row["role"],
            "content": row["content"],
            "timestamp": row["timestamp"]
        }
    return None


def cleanup_old_messages(user_id: int, keep_recent: int = 50) -> int:
    """
    Remove old messages, keeping only the most recent ones.
    
    Args:
        user_id: User ID
        keep_recent: Number of recent messages to keep
    
    Returns:
        int: Number of messages deleted
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    # Get count of messages to delete
    cursor.execute("""
        SELECT COUNT(*) FROM conversation_history
        WHERE user_id = ?
    """, (user_id,))
    
    total_count = cursor.fetchone()[0]
    messages_to_delete = total_count - keep_recent
    
    if messages_to_delete > 0:
        cursor.execute("""
            DELETE FROM conversation_history
            WHERE user_id = ?
            AND id NOT IN (
                SELECT id FROM (
                    SELECT id FROM conversation_history
                    WHERE user_id = ?
                    ORDER BY timestamp DESC
                    LIMIT ?
                )
            )
        """, (user_id, user_id, keep_recent))
        
        deleted_count = cursor.rowcount
        conn.commit()
        logger.info(f"Cleaned up {deleted_count} old messages for user {user_id}")
    else:
        deleted_count = 0
    
    conn.close()
    return deleted_count
