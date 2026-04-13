# Telegram Bot

A Telegram bot with multiple integrated features including weather reporting, speech recognition, system commands, calendar management, AI assistance, and oblique strategies.

## Docker Deployment

### Build and Run with Environment Variables

```bash
# Build the Docker image
docker build -t telegram-bot .

# Run with required environment variables
docker run -d \
  --name telegram-bot \
  -e TOKEN="your_telegram_bot_token_here" \
  -e LLM_API_URL="http://rtn:11444" \
  -e CAL_URL="http://calendar-server:8080" \
  -e CAL_USER="calendar_user" \
  -e CAL_PASS="calendar_password" \
  -v $(pwd)/.cache:/telegram_bot/.cache \
  -v $(pwd)/oblique_strategies:/data/repositories/telegram_bot/oblique_strategies \
  telegram-bot

# Or with a .env file (recommended for production)
docker run -d \
  --name telegram-bot \
  --env-file .env \
  -v $(pwd)/.cache:/telegram_bot/.cache \
  -v $(pwd)/oblique_strategies:/data/repositories/telegram_bot/oblique_strategies \
  telegram-bot
```

### Required Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `TOKEN` | **Yes** | Telegram Bot API token |
| `LLM_API_URL` | No | URL for LLM API (default: `http://rtn:11444`) |
| `CAL_URL` | No | Calendar server URL (for reminders feature) |
| `CAL_USER` | No | Calendar server username |
| `CAL_PASS` | No | Calendar server password |

### Dockerfile Notes

The Dockerfile copies all requirements and source files but does not set environment variables.
You must pass them at runtime using `-e` flags or a `.env` file.

## Features

| Feature | Command(s) | Description |
|---------|------------|-------------|
| **Start** | `/start`, `/ayuda` | Greet the user and initialize the session |
| **Help** | `/help`, `/ayuda` | Display available commands |
| **Weather** | `/weather`, `/tiempo` | Get current weather forecast (temperature, precipitation, etc.) |
| **Speech to Text** | `/habla`, `/talk` | Convert voice messages to text using Google Speech Recognition |
| **System Uptime** | `/uptime` | Display server uptime |
| **System IP** | `/ip` | Display current IP address |
| **GeoIP Lookup** | `/geoip <IP>` | Perform geoIP lookup for a given IP address |
| **Fortune** | `/cita`, `/fortune` | Display a random fortune |
| **Firewall Flush** | `/fwflush` | Flush firewall rules |
| **Firewall Unban** | `/unban <IP>` | Unban a specific IP from fail2ban |
| **Firewall Fail2Ban** | `/fail2ban <action>` | Start or stop fail2ban service |
| **Reminder** | `/remind <time> <message>` | Set a reminder for a specific time or duration |
| **Oblique Strategy** | `/oblique`, `/ob` | Display a random oblique strategy card |
| **AI Assistant** | `/ai <prompt>` | Query the AI assistant with a prompt |

## Environment Variables by Module

### General
- `TOKEN` - Telegram Bot API token (required)

### LLM/AI Module
- `LLM_API_URL` - URL for the LLM API (default: `http://rtn:11444`)

### Calendar Module (Reminders)
- `CAL_URL` - Calendar server URL
- `CAL_USER` - Calendar server username
- `CAL_PASS` - Calendar server password

### Speech Module
- Audio files must be in WAV format. Convert with:
```bash
ffmpeg -i voice_file voice_file.wav
```

### Weather Module
- Uses Open-Meteo API with caching (`.cache` directory)
- Caching enabled with 3600s expiration
- Retry logic with 5 retries and 0.2s backoff factor

### System Module
- SSH access to remote server (for geoiplookup)
- fail2ban service
- ffmpeg for audio conversion

## Classes for Modification

To add new functionality to the bot, modify the following classes and functions:

### `calendar/event.py` - Line 4
```python
class Event:
    """Class for storing Events."""
```
**Purpose**: Stores event data (time and summary).
**Modify to add**: New event attributes (location, description, attendees, etc.).

### `weather/weather.py` - Line 7
```python
def get_weather_report():
```
**Purpose**: Fetches and formats weather data from Open-Meteo API.
**Modify to add**: Support for multiple locations, additional weather parameters, or different weather APIs.

### `speech/speech_recog.py` - Line 4
```python
def speech_to_text_from_file(file_path) -> str:
```
**Purpose**: Converts audio files to text using Google Speech Recognition.
**Modify to add**: Support for different languages, custom voice profiles, or alternative speech recognition services.

### `system/system_commands.py` - Line 53
```python
def uptime() -> str:
```
**Purpose**: System utility functions for server management and interaction.
**Modify to add**: New system commands, custom scripts, or external API integrations.

### `calendar/calendar_events.py` - Line 71
```python
def get_events(calendar: str) -> list[Event]:
```
**Purpose**: Retrieves calendar events from a specified calendar.  
**Modify to add**: Support for multiple calendars, event filtering, or recurring event handling.

### `calendar/calendar_events.py` - Line 48
```python
def connect(calendar: str) -> caldav.lib.dav.Calendar:
```
**Purpose**: Connects to calendar using credentials from environment variables.  
**Modify to add**: Support for multiple calendar accounts, OAuth authentication, or calendar sync.

### `system/system_commands.py` - Line 79
```python
def reminder(input_text):
```
**Purpose**: Handles reminder scheduling using systemd.  
**Modify to add**: Persistent storage, reminder notifications, or reminder categories.

### `system/system_commands.py` - Line 94
```python
def geoip(input_text: str) -> str:
```
**Purpose**: Performs geoIP lookup for a given IP address.  
**Modify to add**: Support for multiple geoIP databases, additional location fields, or async processing.

### `llm/llm_api.py` - Line 15
```python
def query_llm(prompt: str) -> str:
```
**Purpose**: Sends queries to the LLM API and returns responses.  
**Modify to add**: Support for different models, streaming responses, or custom system prompts.

### `llm/llm_api.py` - Line 62
```python
def query_llm_streaming(prompt: str) -> str:
```
**Purpose**: Sends streaming queries to the LLM API.  
**Modify to add**: Real-time response handling, response chunking, or WebSocket support.

### `validators.py` - Line 12
```python
@dataclass
class ValidationResult:
```
**Purpose**: Stores validation results with status and messages.  
**Modify to add**: Additional validation metadata, error codes, or validation chains.

### `validators.py` - Line 19
```python
class ValidationError(Exception):
```
**Purpose**: Custom exception for validation errors.  
**Modify to add**: Error categories, recovery suggestions, or validation context.

### `validators.py` - Line 33
```python
class IPValidator:
```
**Purpose**: Validates IP address format with octet checking.  
**Modify to add**: IPv6 support, CIDR notation, or IP range validation.

### `validators.py` - Line 72
```python
class TimeValidator:
```
**Purpose**: Validates time format (hh:mm or Xsm/Xmh/Xsh).  
**Modify to add**: Date validation, timezone support, or ISO 8601 format.

### `validators.py` - Line 102
```python
class InputValidator:
```
**Purpose**: General input validation utilities.  
**Modify to add**: Email validation, phone number validation, or custom validators.

## Docker

### Build docker image

```bash
docker build -t "telegram_bot:0.1" .
```

### Run docker image

```bash
docker run -d -e TOKEN="" -e CAL_URL="" -e CAL_USER="" -e CAL_PASS="" --name telegram_bot telegram_bot:0.1
```

## Requirements

### Project-wide
- Python 3.x
- Telegram Bot API

### Speech Module
- Audio files must be in WAV format. Convert with:
```bash
ffmpeg -i voice_file voice_file.wav
```

### Calendar Module
- caldav library
- Calendar server credentials (URL, username, password)

### Weather Module
- Open-Meteo API access
- requests-cache library
- retry-requests library

### System Module
- SSH access to remote server
- fail2ban service
- ffmpeg for audio conversion

### LLM/AI Module
- requests library
- LLM API endpoint configured via `LLM_API_URL`

## Input Validation

The bot uses a centralized validation system to prevent injection attacks and ensure data integrity:

- **IPValidator**: Validates IPv4 addresses with octet checking (0-255)
- **TimeValidator**: Validates time formats (hh:mm or Xsm/Xmh/Xsh)
- **InputValidator**: Validates general input text with length constraints
- **sanitize_input**: Removes null bytes and control characters

## License

MIT License
