"""Calendar event management module for the Telegram bot.

This module handles calendar operations including getting, adding, and printing events.
"""
import os
import datetime
from datetime import datetime, timedelta
import locale
import caldav
from caldav.elements import dav, cdav
from event import Event


class CalendarError(Exception):
    """Base exception for calendar-related errors."""
    pass


class CalendarConnectionError(CalendarError):
    """Raised when calendar connection fails."""
    pass


class CalendarCredentialsError(CalendarError):
    """Raised when calendar credentials are invalid."""
    pass


def get_credentials() -> tuple[str, str, str]:
    """Get credentials from environment variables.
    
    Returns:
        tuple: (url, user, password)
        
    Raises:
        CalendarCredentialsError: If any credential is missing
    """
    url = os.environ.get("CAL_URL")
    user = os.environ.get("CAL_USER")
    password = os.environ.get("CAL_PASS")
    
    if not all([url, user, password]):
        raise CalendarCredentialsError("Missing calendar credentials. Set CAL_URL, CAL_USER, and CAL_PASS environment variables.")
    
    return url, user, password


def connect(calendar: str) -> caldav.lib.dav.Calendar:
    """Connect to calendar using credentials from environment variables.
    
    Args:
        calendar: Calendar name to connect to
        
    Returns:
        Calendar object from caldav
        
    Raises:
        CalendarCredentialsError: If credentials are missing
        CalendarConnectionError: If connection fails
    """
    try:
        url, user, password = get_credentials()
        client = caldav.DAVClient(url=url, username=user, password=password)
        return client.principal().calendar(name=calendar)
    except CalendarCredentialsError as e:
        raise CalendarCredentialsError(f"Calendar connection failed: {e}")
    except Exception as e:
        raise CalendarConnectionError(f"Failed to connect to calendar '{calendar}': {e}")


def get_events(calendar: str) -> list[Event]:
    """Get today's events for a calendar.
    
    Args:
        calendar: Calendar name to fetch events from
        
    Returns:
        List of Event objects for today
        
    Raises:
        CalendarCredentialsError: If credentials are missing
        CalendarConnectionError: If connection fails
    """
    event_list: list[Event] = []
    try:
        cal = connect(calendar)
        
        # Fetch todays events
        events = cal.date_search(datetime.date.today(), datetime.date.today() + timedelta(days=1))
        
        # Get the events and push them to stdout
        for event in events:
            event.load()
            e = event.instance.vevent
            event_list.append(Event(e.dtstart.value.strftime('%H:%M'), e.summary.value))
        return event_list
    except CalendarCredentialsError as e:
        raise CalendarCredentialsError(f"Failed to get events from calendar '{calendar}': {e}")
    except CalendarConnectionError as e:
        raise CalendarConnectionError(f"Failed to get events from calendar '{calendar}': {e}")
    except Exception as e:
        raise CalendarError(f"Unexpected error getting events from calendar '{calendar}': {e}")


def add_event(calendar: str, summary: str, start: str, duration: int) -> None:
    """Add a new event to the calendar.
    
    Args:
        calendar: Calendar name to add event to
        summary: Event summary/title
        start: Start time in voice format (e.g., "10:00" or "2pm")
        duration: Duration in hours
        
    Raises:
        CalendarCredentialsError: If credentials are missing
        CalendarConnectionError: If connection fails
        ValueError: If date parsing fails
    """
    try:
        event_start = parse_date_from_voice(start)
        event_end = event_start + timedelta(hours=duration)
        
        cal = connect(calendar)
        cal.save_event(dtstart=event_start,
                       dtend=event_end,
                       summary=summary)
    except CalendarCredentialsError as e:
        raise CalendarCredentialsError(f"Failed to add event to calendar '{calendar}': {e}")
    except CalendarConnectionError as e:
        raise CalendarConnectionError(f"Failed to add event to calendar '{calendar}': {e}")
    except ValueError as e:
        raise ValueError(f"Failed to add event: {e}")
    except Exception as e:
        raise CalendarError(f"Unexpected error adding event to calendar '{calendar}': {e}")


def parse_date_from_voice(date_text: str) -> datetime:
    """Parse date from voice input.
    
    Args:
        date_text: Date string in format "dd de MMMM de YYYY a las HH:MM"
        
    Returns:
        Parsed datetime object
        
    Raises:
        ValueError: If date format is invalid
    """
    locale.setlocale(locale.LC_TIME, 'es_ES.UTF-8')
    PATTERN = "%d de %B de %Y a las %H:%M"
    try:
        return datetime.strptime(date_text, PATTERN)
    except ValueError as e:
        raise ValueError(f"Invalid date format: {date_text}. Expected format: 'dd de MMMM de YYYY a las HH:MM'") from e


def print_events(calendar: str) -> None:
    """Print all events for a calendar.
    
    Args:
        calendar: Calendar name to print events from
        
    Raises:
        CalendarCredentialsError: If credentials are missing
        CalendarConnectionError: If connection fails
    """
    try:
        cal = connect(calendar)
        for event in cal.events():
            ical_text = event.data
            print(ical_text)
    except CalendarCredentialsError as e:
        raise CalendarCredentialsError(f"Failed to print events from calendar '{calendar}': {e}")
    except CalendarConnectionError as e:
        raise CalendarConnectionError(f"Failed to print events from calendar '{calendar}': {e}")
    except Exception as e:
        raise CalendarError(f"Unexpected error printing events from calendar '{calendar}': {e}")


if __name__ == "__main__":
    try:
        today_events = get_events("Personal")
        print(today_events)
    except CalendarCredentialsError as e:
        print(f"Calendar credentials error: {e}")
    except CalendarConnectionError as e:
        print(f"Calendar connection error: {e}")
    except CalendarError as e:
        print(f"Calendar error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")
