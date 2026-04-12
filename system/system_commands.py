import re
import subprocess
import requests
import json
import random
import os
from typing import Optional

class SystemCommandError(Exception):
    """Base exception for system command errors."""
    pass

class SubprocessError(SystemCommandError):
    """Raised when a subprocess call fails."""
    pass

class NetworkError(SystemCommandError):
    """Raised when a network request fails."""
    pass

class FileNotFoundError(SystemCommandError):
    """Raised when a required file is not found."""
    pass

class ValidationError(SystemCommandError):
    """Raised when input validation fails."""
    pass

def _safe_subprocess_run(cmd: list[str], timeout: int = 30) -> subprocess.CompletedProcess:
    """Safely run a subprocess command with timeout.
    
    Args:
        cmd: Command list to execute
        timeout: Timeout in seconds
        
    Returns:
        CompletedProcess result
        
    Raises:
        SubprocessError: If command fails or times out
    """
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        if result.returncode != 0:
            raise SubprocessError(f"Command failed: {' '.join(cmd)}\nstderr: {result.stderr}")
        return result
    except subprocess.TimeoutExpired:
        raise SubprocessError(f"Command timed out after {timeout}s: {' '.join(cmd)}")
    except Exception as e:
        raise SubprocessError(f"Subprocess execution failed: {e}")

def uptime() -> str:
    """Display server uptime.
    
    Returns:
        Server uptime information
    """
    try:
        return subprocess.check_output(["uptime"]).decode('utf-8')
    except Exception as e:
        raise SubprocessError(f"Failed to get uptime: {e}")

def ip() -> str:
    """Get the current IP address.
    
    Returns:
        IP address string
        
    Raises:
        NetworkError: If network request fails
    """
    try:
        response = requests.get('https://ifconfig.me', timeout=10)
        response.raise_for_status()
        return "IP: " + response.text
    except requests.RequestException as e:
        raise NetworkError(f"Failed to fetch IP address: {e}")

def geoip(input_text: str) -> str:
    """Perform geoIP lookup for a given IP address.
    
    Args:
        input_text: User input containing the IP address (prefix 'geoip ' should be stripped)
        
    Returns:
        GeoIP lookup result
        
    Raises:
        ValidationError: If IP address is invalid
        SubprocessError: If SSH command fails
    """
    try:
        ip = input_text[7:].strip()
        if not ip:
            raise ValidationError("IP address cannot be empty")
        if not re.match(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$', ip):
            raise ValidationError(f"Invalid IP address format: {ip}")
        result = _safe_subprocess_run(
            ["ssh", "reverse", "geoiplookup", ip],
            timeout=30
        )
        return result.stdout
    except ValidationError as e:
        raise ValidationError(f"GeoIP lookup failed: {e}")
    except SubprocessError as e:
        raise SubprocessError(f"GeoIP lookup failed: {e}")

def fortune() -> str:
    """Get a random fortune message.
    
    Returns:
        Fortune message text
        
    Raises:
        SubprocessError: If fortune command fails
    """
    try:
        result = _safe_subprocess_run(
            ["fortune", "-a"],
            timeout=10
        )
        return result.stdout
    except SubprocessError as e:
        raise SubprocessError(f"Fortune command failed: {e}")

def firewall_flush() -> str:
    """Flush firewall rules.
    
    Returns:
        Result of the firewall flush operation
        
    Raises:
        SubprocessError: If SSH command fails
    """
    try:
        result = _safe_subprocess_run(
            ["ssh", "reverse", "sudo", "fwflush"],
            timeout=30
        )
        return result.stdout
    except SubprocessError as e:
        raise SubprocessError(f"Firewall flush failed: {e}")

def firewall_unban(input_text: str) -> str:
    """Unban a specific IP from fail2ban.
    
    Args:
        input_text: User input containing the IP address (prefix 'fwflush ' should be stripped)
        
    Returns:
        Result of the unban operation
        
    Raises:
        ValidationError: If input is invalid
        SubprocessError: If SSH command fails
    """
    try:
        jail_and_ip = input_text[7:].strip()
        if not jail_and_ip:
            raise ValidationError("IP address cannot be empty")
        if not re.match(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$', jail_and_ip):
            raise ValidationError(f"Invalid IP address format: {jail_and_ip}")
        result = _safe_subprocess_run(
            ["ssh", "reverse", "sudo", "unban", jail_and_ip],
            timeout=30
        )
        return result.stdout
    except ValidationError as e:
        raise ValidationError(f"Unban failed: {e}")
    except SubprocessError as e:
        raise SubprocessError(f"Unban failed: {e}")

def firewall_fail2ban(input_text: str) -> str:
    """Start or stop fail2ban service.
    
    Args:
        input_text: User input containing the action (prefix 'fail2ban ' should be stripped)
        
    Returns:
        Result of the fail2ban operation
        
    Raises:
        ValidationError: If input is invalid
        SubprocessError: If SSH command fails
    """
    try:
        start_stop = input_text[10:].strip()
        if not start_stop:
            raise ValidationError("Action cannot be empty")
        if start_stop not in ["start", "stop"]:
            raise ValidationError(f"Invalid action. Use 'start' or 'stop'. Got: {start_stop}")
        result = _safe_subprocess_run(
            ["ssh", "reverse", "sudo", "f2b", start_stop],
            timeout=30
        )
        return result.stdout
    except ValidationError as e:
        raise ValidationError(f"Fail2ban operation failed: {e}")
    except SubprocessError as e:
        raise SubprocessError(f"Fail2ban operation failed: {e}")

def audio_to_wav(file_path: str) -> str:
    """Convert audio file to WAV format.
    
    Args:
        file_path: Path to the input audio file
        
    Returns:
        Path to the converted WAV file
        
    Raises:
        FileNotFoundError: If input file does not exist
        RuntimeError: If ffmpeg conversion fails
    """
    if not file_path or not os.path.exists(file_path):
        raise FileNotFoundError(f"Input file not found: {file_path}")
    
    output_file = "/tmp/voice_file.wav"
    try:
        result = subprocess.run(
            ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-i", file_path, output_file],
            capture_output=True,
            text=True,
            timeout=60
        )
        if result.returncode != 0:
            raise RuntimeError(f"ffmpeg conversion failed: {result.stderr}")
        return output_file
    except subprocess.TimeoutExpired:
        raise RuntimeError(f"ffmpeg conversion timed out after 60s")
    except Exception as e:
        raise RuntimeError(f"ffmpeg conversion failed: {e}")

def talk(input_text: str) -> None:
    """Send a voice message response.
    
    Args:
        input_text: User input containing the message text (prefix 'talk ' should be stripped)
        
    Raises:
        ValidationError: If input is invalid
        SubprocessError: If voice message command fails
    """
    try:
        input_text = input_text[7:].strip()
        if not input_text:
            raise ValidationError("Message cannot be empty")
        if len(input_text) > 1000:
            raise ValidationError("Message too long (max 1000 characters)")
        result = subprocess.run(
            ["/usr/local/bin/assistant/ratoncio_send_voice", input_text],
            capture_output=True,
            text=True,
            timeout=30
        )
    except ValidationError as e:
        raise ValidationError(f"Voice message failed: {e}")
    except subprocess.TimeoutExpired:
        raise SubprocessError("Voice message send timed out")
    except Exception as e:
        raise SubprocessError(f"Voice message send failed: {e}")

def reminder(input_text: str) -> Optional[str]:
    """Set a reminder for a specific time or duration.
    
    Args:
        input_text: User input containing time and message
        
    Returns:
        'OK' if successful, help message if parsing fails
        
    Raises:
        SubprocessError: If systemd-run command fails
    """
    help_message = "/remind hh:mm message\n/remind XXm message, for a message after XX minutes (s, m and h for seconds, minutes and hours)"
    send_message_command = "/usr/local/bin/assistant/ratoncio_send_msg"
    try:
        input_text = input_text[8:]
        time, message = input_text.split(None, 1)
        message = "\u23F0 " + message  # clock emoji
    except (IndexError, ValueError):
        return help_message
    
    # hh:mm match
    if re.match(r'^\d{1,2}:\d{2}\s', input_text):
        try:
            subprocess.run(["sudo", "/usr/bin/systemd-run", "--on-calendar", f'{time}:00', send_message_command, message],
                         timeout=30)
            return "OK"
        except subprocess.TimeoutExpired:
            raise SubprocessError("Reminder setup timed out")
        except Exception as e:
            raise SubprocessError(f"Reminder setup failed: {e}")
    
    # after X seconds, minutes or hours match
    elif re.match(r'^\d+[smh]\s', input_text):
        try:
            subprocess.run(["sudo", "/usr/bin/systemd-run", "--on-active", time, send_message_command, message],
                         timeout=30)
            return "OK"
        except subprocess.TimeoutExpired:
            raise SubprocessError("Reminder setup timed out")
        except Exception as e:
            raise SubprocessError(f"Reminder setup failed: {e}")
    
    else:
        return f"Parse error in time format\n{help_message}"

def oblique() -> str:
    """Get a random oblique strategy card.
    
    Returns:
        Random oblique strategy card text or error message
        
    Raises:
        FileNotFoundError: If JSON file does not exist
        json.JSONDecodeError: If JSON file is malformed
    """
    ob_st_file = '/data/repositories/telegram_bot/oblique_strategies/oblique_strategies_2015.json'
    
    if not os.path.exists(ob_st_file):
        raise FileNotFoundError(f"Oblique strategies file not found: {ob_st_file}")
    
    try:
        with open(ob_st_file, 'r') as file:
            # Load the JSON data as a Python list
            data_list = json.load(file)

            if isinstance(data_list, list) and data_list:  # Check if it's a non-empty list
                # Use random.choice() to pick one random dictionary from the list
                random_entry = random.choice(data_list)
                
                # Extract the value from the randomly selected dictionary
                if "card" in random_entry:
                    return random_entry["card"]
                else:
                    return "Error: The random entry did not have a 'card' key."
                    
            elif not data_list:
                return "Error: The JSON list is empty."
            else:
                return "Error: JSON file did not contain a list of objects."

    except json.JSONDecodeError as e:
        raise json.JSONDecodeError(f"Could not decode JSON from the file '{ob_st_file}'. Check file format.", e.doc, e.pos)
    except Exception as e:
        raise SystemCommandError(f"Unexpected error in oblique: {e}")

if __name__ == "__main__":
    print(uptime())
    print(ip())
    print(fortune())
    audio_to_wav("/tmp/voice_file.ogg")
