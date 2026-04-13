"""Input validation module for the Telegram bot.

This module provides centralized validation functions to prevent injection attacks
and ensure data integrity across the application.
"""
import re
from typing import Optional, Union
from dataclasses import dataclass


@dataclass
class ValidationResult:
    """Result of a validation operation."""
    is_valid: bool
    message: str
    field: Optional[str] = None


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


class IPValidator:
    """Validator for IP address format.
    
    Provides comprehensive IPv4 validation with octet checking.
    """
    
    @staticmethod
    def validate(ip: str) -> ValidationResult:
        """Validate IP address format.
        
        Args:
            ip: IP address string to validate
            
        Returns:
            ValidationResult with is_valid and message
            
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
        
        return ValidationResult(is_valid=True, message=f"Valid IP address: {ip}", field="ip")


class TimeValidator:
    """Validator for time format (hh:mm or Xsm/Xmh/Xsh)."""
    
    @staticmethod
    def validate(time_str: str) -> ValidationResult:
        """Validate time format.
        
        Args:
            time_str: Time string to validate
            
        Returns:
            ValidationResult with is_valid and message
            
        Raises:
            ValidationError: If time format is invalid
        """
        if not isinstance(time_str, str):
            raise ValidationError(f"Invalid time: expected string, got {type(time_str).__name__}", "time")
        
        # Pattern for hh:mm format
        hhmm_pattern = r'^\d{1,2}:\d{2}\s'
        
        if not re.match(hhmm_pattern, time_str):
            raise ValidationError(f"Invalid time format: {time_str}. Expected 'hh:mm'", "time")
        
        return ValidationResult(is_valid=True, message=f"Valid time format: {time_str}", field="time")




class InputValidator:
    """General input validation utilities."""
    
    @staticmethod
    def validate_input(input_text: str, min_length: int = 0, max_length: int = 1000) -> ValidationResult:
        """Validate general input text.
        
        Args:
            input_text: Input text to validate
            min_length: Minimum length (default: 0)
            max_length: Maximum length (default: 1000)
            
        Returns:
            ValidationResult with is_valid and message
        """
        if not isinstance(input_text, str):
            raise ValidationError(f"Invalid input: expected string, got {type(input_text).__name__}", "input")
        
        if len(input_text) < min_length:
            raise ValidationError(f"Input too short (minimum {min_length} characters)", "input")
        if len(input_text) > max_length:
            raise ValidationError(f"Input too long (maximum {max_length} characters)", "input")
        
        return ValidationResult(is_valid=True, message=f"Valid input ({len(input_text)} characters)", field="input")
    
    @staticmethod
    def sanitize_input(input_text: str, max_length: int = 1000) -> str:
        """Sanitize input text by removing potentially harmful characters.
        
        Args:
            input_text: Input text to sanitize
            max_length: Maximum length after sanitization
            
        Returns:
            Sanitized input text
        """
        # Remove null bytes and control characters
        sanitized = re.sub(r'[\x00-\x1f\x7f]', '', input_text)
        # Truncate to max length
        if len(sanitized) > max_length:
            sanitized = sanitized[:max_length]
        return sanitized
    
    @staticmethod
    def validate_with_error(value: str, validator_func, field_name: Optional[str] = None) -> None:
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


