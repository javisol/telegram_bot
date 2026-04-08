"""Input validation module for the Telegram bot.

This module provides centralized validation functions to prevent injection attacks
and ensure data integrity across the application.
"""
import re
from typing import Optional


class ValidationError(Exception):
    """Custom exception for validation errors.
    
    Attributes:
        message: Error message
        field: Name of the field that failed validation
    """
    
    def __init__(self, message: str, field: Optional[str] = None):
        self.message = message
        self.field = field
        super().__init__(self.message)


def validate_ip(ip: str) -> bool:
    """Validate IP address format.
    
    Args:
        ip: IP address string to validate
        
    Returns:
        True if valid IPv4 format, False otherwise
        
    Raises:
        ValidationError: If IP is invalid
    """
    if not isinstance(ip, str):
        raise ValidationError(f"Invalid IP address: expected string, got {type(ip).__name__}", "ip")
    
    pattern = r'^(\d{1,3}\.){3}\d{1,3}$'
    if not re.match(pattern, ip):
        raise ValidationError(f"Invalid IP address format: {ip}", "ip")
    
    # Check each octet is 0-255
    octets = ip.split('.')
    for i, octet in enumerate(octets, 1):
        try:
            octet_int = int(octet)
            if octet_int > 255:
                raise ValidationError(f"IP octet {i} exceeds maximum value of 255: {octet}", "ip")
        except ValueError:
            raise ValidationError(f"Invalid IP octet {i}: {octet} is not a valid number", "ip")
    
    return True


def validate_time(time_str: str) -> bool:
    """Validate time format (hh:mm or Xsm/Xmh/Xsh).
    
    Args:
        time_str: Time string to validate
        
    Returns:
        True if valid time format, False otherwise
        
    Raises:
        ValidationError: If time format is invalid
    """
    if not isinstance(time_str, str):
        raise ValidationError(f"Invalid time: expected string, got {type(time_str).__name__}", "time")
    
    # Pattern for hh:mm format
    hhmm_pattern = r'^\d{1,2}:\d{2}\s'
    # Pattern for duration format (Xsm, Xmh, Xsh)
    duration_pattern = r'^\d+[smh]\s'
    
    if not re.match(hhmm_pattern, time_str) and not re.match(duration_pattern, time_str):
        raise ValidationError(f"Invalid time format: {time_str}. Expected 'hh:mm' or 'Xsm/Xmh/Xsh'", "time")
    
    return True


def validate_calendar_name(calendar: str) -> bool:
    """Validate calendar name.
    
    Args:
        calendar: Calendar name string to validate
        
    Returns:
        True if valid calendar name, False otherwise
        
    Raises:
        ValidationError: If calendar name is invalid
    """
    if not isinstance(calendar, str):
        raise ValidationError(f"Invalid calendar name: expected string, got {type(calendar).__name__}", "calendar")
    
    # Allow alphanumeric, spaces, hyphens, and underscores
    pattern = r'^[a-zA-Z0-9\s\-_]+$'
    if not re.match(pattern, calendar):
        raise ValidationError(f"Invalid calendar name: {calendar}. Only alphanumeric, spaces, hyphens, and underscores allowed", "calendar")
    
    return True


def validate_summary(summary: str) -> bool:
    """Validate event summary.
    
    Args:
        summary: Event summary string to validate
        
    Returns:
        True if valid summary, False otherwise
        
    Raises:
        ValidationError: If summary is invalid
    """
    if not isinstance(summary, str):
        raise ValidationError(f"Invalid summary: expected string, got {type(summary).__name__}", "summary")
    
    # Allow printable characters, max 255 chars
    if len(summary) > 255:
        raise ValidationError(f"Summary exceeds maximum length of 255 characters: {len(summary)}", "summary")
    if not all(32 <= ord(c) <= 126 for c in summary):
        raise ValidationError("Summary contains invalid characters. Only printable ASCII characters allowed", "summary")
    
    return True


def validate_duration(duration: str) -> bool:
    """Validate duration format (Xsm, Xmh, Xsh).
    
    Args:
        duration: Duration string to validate
        
    Returns:
        True if valid duration format, False otherwise
        
    Raises:
        ValidationError: If duration format is invalid
    """
    if not isinstance(duration, str):
        raise ValidationError(f"Invalid duration: expected string, got {type(duration).__name__}", "duration")
    
    pattern = r'^\d+[smh]$'
    if not re.match(pattern, duration):
        raise ValidationError(f"Invalid duration format: {duration}. Expected 'Xsm' (seconds), 'Xmh' (minutes), or 'Xsh' (hours)", "duration")
    
    return True


def validate_date(date_text: str) -> bool:
    """Validate date format for voice input.
    
    Args:
        date_text: Date string to validate
        
    Returns:
        True if valid date format, False otherwise
        
    Raises:
        ValidationError: If date format is invalid
    """
    if not isinstance(date_text, str):
        raise ValidationError(f"Invalid date: expected string, got {type(date_text).__name__}", "date")
    
    # Pattern: "%d de %B de %Y a las %H:%M"
    pattern = r'^\d{1,2} de [A-Za-z]+ de \d{4} a las \d{2}:\d{2}$'
    if not re.match(pattern, date_text):
        raise ValidationError(f"Invalid date format: {date_text}. Expected 'dd de MMMM de YYYY a las HH:MM'", "date")
    
    return True


def validate_url(url: str) -> bool:
    """Validate URL format.
    
    Args:
        url: URL string to validate
        
    Returns:
        True if valid URL format, False otherwise
        
    Raises:
        ValidationError: If URL format is invalid
    """
    if not isinstance(url, str):
        raise ValidationError(f"Invalid URL: expected string, got {type(url).__name__}", "url")
    
    pattern = r'^https?://[^\s/$.?#].[^\s]*$'
    if not re.match(pattern, url):
        raise ValidationError(f"Invalid URL format: {url}. Must start with http:// or https://", "url")
    
    return True


def validate_username(username: str) -> bool:
    """Validate username format.
    
    Args:
        username: Username string to validate
        
    Returns:
        True if valid username format, False otherwise
        
    Raises:
        ValidationError: If username format is invalid
    """
    if not isinstance(username, str):
        raise ValidationError(f"Invalid username: expected string, got {type(username).__name__}", "username")
    
    # Allow alphanumeric and underscores, 1-32 chars
    pattern = r'^[a-zA-Z0-9_]{1,32}$'
    if not re.match(pattern, username):
        raise ValidationError(f"Invalid username format: {username}. Only alphanumeric characters and underscores allowed (1-32 chars)", "username")
    
    return True


def validate_password(password: str) -> bool:
    """Validate password format.
    
    Args:
        password: Password string to validate
        
    Returns:
        True if valid password format, False otherwise
        
    Raises:
        ValidationError: If password format is invalid
    """
    if not isinstance(password, str):
        raise ValidationError(f"Invalid password: expected string, got {type(password).__name__}", "password")
    
    # Minimum 8 characters, at least one letter and one digit
    if len(password) < 8:
        raise ValidationError(f"Password must be at least 8 characters long (current length: {len(password)})", "password")
    if not re.search(r'[a-zA-Z]', password):
        raise ValidationError("Password must contain at least one letter", "password")
    if not re.search(r'\d', password):
        raise ValidationError("Password must contain at least one digit", "password")
    
    return True


def validate_with_error(value, validator_func, field_name: Optional[str] = None) -> None:
    """Validate a value and raise ValidationError if invalid.
    
    Args:
        value: Value to validate
        validator_func: Validation function to call
        field_name: Name of the field for error messages
        
    Raises:
        ValidationError: If validation fails
    """
    if not isinstance(value, str):
        raise ValidationError(f"Invalid {field_name or 'value'}: expected string, got {type(value).__name__}", field_name)
    
    if not validator_func(value):
        raise ValidationError(f"Invalid {field_name or 'value'}", field_name)
