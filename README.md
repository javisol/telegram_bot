# Telegram Bot

A Telegram bot with multiple integrated features including weather reporting, speech recognition, system commands, calendar management, and oblique strategies.

## Load env vars

```bash
set -o allexport;source .env;set +o allexport
```

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
| **Talk** | `/habla`, `/talk` | Send a voice message response |

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

### `system/system_commands.py` - Line 7
```python
def uptime():
```
**Purpose**: System utility functions for server management and interaction.  
**Modify to add**: New system commands, custom scripts, or external API integrations.

### `calendar/calendar_events.py` - Line 19
```python
def get_events(calendar: str) -> list:
```
**Purpose**: Retrieves calendar events from a specified calendar.  
**Modify to add**: Support for multiple calendars, event filtering, or recurring event handling.

### `calendar/calendar_events.py` - Line 33
```python
def add_event(calendar, summary, start, duration):
```
**Purpose**: Creates new calendar events.  
**Modify to add**: Event categories, attachments, or custom event properties.

### `system/system_commands.py` - Line 51
```python
def reminder(input_text):
```
**Purpose**: Handles reminder scheduling using systemd.  
**Modify to add**: Persistent storage, reminder notifications, or reminder categories.

### `system/system_commands.py` - Line 72
```python
def oblique():
```
**Purpose**: Displays random oblique strategy cards from JSON files.  
**Modify to add**: Custom strategy categories, user-specific strategies, or strategy generation.

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
