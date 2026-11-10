"""
SQLite database operations for conversation context storage with Thread Support.
"""
import os
import sqlite3
import logging
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)

DB_PATH = os.environ.get("LLM_CONVERSATION_DB_PATH", "data/llm_conversation.db")

def get_connection() -> sqlite3.Connection:
    db_dir = os.path.dirname(DB_PATH)
    if db_dir and not os.path.exists(db_dir):
        os.makedirs(db_dir)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    init_tables(conn)
    return conn

def init_tables(conn: sqlite3.Connection) -> None:
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS conversation_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            thread_id TEXT NOT NULL DEFAULT 'General',
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            message_index INTEGER DEFAULT 0
        )
    """)
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_user_thread ON conversation_history(user_id, thread_id)
    """)
    conn.commit()


def get_user_threads(user_id: int) -> List[str]:
    """Devuelve los temas/hilos únicos creados por el usuario."""
    conn = get_connection()
    cursor = conn.cursor()
    # Quitamos el filtro temporalmente para ver qué se está guardando en la DB
    cursor.execute("""
        SELECT DISTINCT thread_id FROM conversation_history 
        WHERE user_id = ?
    """, (user_id,))
    threads = [row["thread_id"] for row in cursor.fetchall()]
    conn.close()
    return threads


def get_history(user_id: int, thread_id: str = "General", limit: int = 100) -> List[Dict]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT role, content FROM conversation_history
        WHERE user_id = ? AND thread_id = ?
        ORDER BY timestamp DESC LIMIT ?
    """, (user_id, thread_id, limit))
    rows = cursor.fetchall()
    messages = [{"role": row["role"], "content": row["content"]} for row in rows]
    messages.reverse()
    conn.close()
    return messages

def append_message(user_id: int, thread_id: str, role: str, content: str) -> int:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO conversation_history (user_id, thread_id, role, content)
        VALUES (?, ?, ?, ?)
    """, (user_id, thread_id, role, content))
    message_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return message_id

def clear_user_history(user_id: int, thread_id: Optional[str] = None) -> None:
    conn = get_connection()
    cursor = conn.cursor()
    if thread_id:
        cursor.execute("DELETE FROM conversation_history WHERE user_id = ? AND thread_id = ?", (user_id, thread_id))
    else:
        cursor.execute("DELETE FROM conversation_history WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()

