# LLM API Module

This module provides LLM API integration with optional conversation context tracking for multi-turn conversations.

## Overview

The `llm_api` module forwards queries to an external LLM API (e.g., Raton) and optionally maintains conversation history per user for context-aware responses.

## Features

- **Single-turn queries**: Basic `query_llm(prompt)` for independent queries
- **Multi-turn conversations**: `query_llm(prompt, context=[])` for context-aware responses
- **Persistent storage**: SQLite database stores conversation history per user
- **Backward compatible**: Existing code continues to work without changes

## Files

| File | Description |
|------|-------------|
| `llm_api.py` | Main LLM API integration with optional context support |
| `conversation_context.py` | High-level conversation context manager |
| `conversation_context_db.py` | SQLite database operations |
| `requirements.txt` | Dependencies (currently just `requests`) |

## Usage

### Single-turn Query (Backward Compatible)

```python
from llm import llm_api

# Simple query - works as before
response = llm_api.query_llm("Hello, how are you?")
print(response)
```

### Multi-turn Conversation

```python
from llm import llm_api
from llm.conversation_context import ConversationContextManager

# Initialize conversation context manager
user_id = 12345
context_manager = ConversationContextManager(user_id)

# Get or initialize conversation history
history = context_manager.get_or_create()

# Append user message
context_manager.append("user", "What is the capital of France?")

# Get conversation context (last 20 messages by default)
context = context_manager.get_context(max_messages=20)

# Call LLM API with context
response = llm_api.query_llm("How are you?", context=context)
print(response)

# Optionally save assistant response back to history
context_manager.append("assistant", response)
```

### Using the Context Manager Directly

```python
from llm.conversation_context import ConversationContextManager

# Create manager for a user
manager = ConversationContextManager(user_id=12345)

# Get conversation history
history = manager.get()

# Append messages
manager.append("user", "Hello!")
manager.append("assistant", "Hi there!")

# Get limited context for LLM API
context = manager.get_context(max_messages=10)

# Get message count
count = manager.get_message_count()

# Clear conversation
manager.clear()
```

## Database Schema

```sql
CREATE TABLE conversation_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    role TEXT NOT NULL,
    content TEXT NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    message_index INTEGER DEFAULT 0
);

CREATE INDEX idx_user_id ON conversation_history(user_id);
CREATE INDEX idx_timestamp ON conversation_history(timestamp);
```

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `LLM_CONVERSATION_DB_PATH` | `data/llm_conversation.db` | Path to SQLite database |

### Python Code Configuration

```python
from llm.conversation_context import ConversationContextManager

# Create with custom history limit
manager = ConversationContextManager(
    user_id=12345,
    history_limit=15  # Keep last 15 messages in context
)
```

## Message Flow

```
User sends message to /ai
    ↓
Bot extracts user_id
    ↓
ConversationContextManager.get_or_create(user_id)
    ↓
Retrieve conversation history from SQLite
    ↓
Append user message to history
    ↓
Get conversation context (last N messages)
    ↓
Call LLM API with context
    ↓
Receive response
    ↓
(Optionally) Append assistant response to history
    ↓
Send response to user
```

## Backward Compatibility

The `query_llm()` function is backward compatible:

```python
# Old signature (still works)
def query_llm(prompt: str, stream: bool = False) -> str:

# New signature (with optional context)
def query_llm(prompt: str, context: List[Dict] = None, stream: bool = False) -> str:
```

When `context=None` or `context=[]`, the function behaves exactly as before.

## Testing

Run the test suite:

```bash
cd tests/llm
python -m pytest test_conversation_context.py -v
```

## Example: Multi-turn Conversation

```
User: "What is 2+2?"
Assistant: "2+2 equals 4."

User: "And 3+3?"
Assistant: "3+3 equals 6."

User: "So 2+2=4 and 3+3=6?"
Assistant: "Yes, that's correct!"
```

The assistant can reference previous messages to maintain context.

## Future Enhancements

Potential future features:

- **Analytics**: Track conversation length, frequency, popular topics
- **Export**: Allow users to export their conversation history
- **Search**: Enable searching through conversation history
- **Summarization**: Auto-summarize long conversations
- **Role-based access**: Admin can view multiple users' histories

## License

Part of the Telegram Bot project.
