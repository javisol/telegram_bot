import re
import subprocess
import requests
import json
import random

def uptime() -> str:
    """Display server uptime.
    
    Returns:
        Server uptime information
    """
    return subprocess.check_output(["uptime"]).decode('utf-8')

def ip():
    return("IP: " + requests.get('https://ifconfig.me').text)

def geoip(input_text: str) -> str:
    """Perform geoIP lookup for a given IP address.
    
    Args:
        input_text: User input containing the IP address
        
    Returns:
        GeoIP lookup result
    """
    ip = input_text[5:]
    result = subprocess.run(
        ["ssh", "reverse", "geoiplookup", ip],
        capture_output=True,
        text=True
    )
    return result.stdout

def fortune():
    result = subprocess.run(["fortune -a"], shell=True, capture_output=True, text=True)
    return result.stdout

def firewall_flush() -> str:
    """Flush firewall rules.
    
    Returns:
        Result of the firewall flush operation
    """
    result = subprocess.run(
        ["ssh", "reverse", "sudo", "fwflush"],
        capture_output=True,
        text=True
    )
    return result.stdout

def firewall_unban(input_text: str) -> str:
    """Unban a specific IP from fail2ban.
    
    Args:
        input_text: User input containing the IP address
        
    Returns:
        Result of the unban operation
    """
    jail_and_ip = input_text[7:]
    result = subprocess.run(
        ["ssh", "reverse", "sudo", "unban", jail_and_ip],
        capture_output=True,
        text=True
    )
    return result.stdout

def firewall_fail2ban(input_text: str) -> str:
    """Start or stop fail2ban service.
    
    Args:
        input_text: User input containing the action (start/stop)
        
    Returns:
        Result of the fail2ban operation
    """
    start_stop = input_text[10:]
    result = subprocess.run(
        ["ssh", "reverse", "sudo", "f2b", start_stop],
        capture_output=True,
        text=True
    )
    return result.stdout

def audio_to_wav(file_path: str) -> str:
    """Convert audio file to WAV format.
    
    Args:
        file_path: Path to the input audio file
        
    Returns:
        Path to the converted WAV file
    """
    output_file = "/tmp/voice_file.wav"
    result = subprocess.run(
        ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-i", file_path, output_file],
        capture_output=True,
        text=True
    )
    if result.returncode != 0:
        raise RuntimeError(f"ffmpeg conversion failed: {result.stderr}")
    return output_file

def talk(input_text: str) -> None:
    """Send a voice message response.
    
    Args:
        input_text: User input containing the message text
    """
    input_text = input_text[7:]
    result = subprocess.run(
        ["/usr/local/bin/assistant/ratoncio_send_voice", input_text],
        capture_output=True,
        text=True
    )

def reminder(input_text):
    help_message = f"/remind hh:mm message\n/remind XXm message, for a message after XX minutes (s, m and h for seconds, minutes and hours)"
    send_message_command = "/usr/local/bin/assistant/ratoncio_send_msg"
    try:
        input_text = input_text[8:]
        time, message = input_text.split(None, 1)
        message = "\u23F0 " + message # clock emoji
    except Exception:
        return help_message
    # hh:mm match
    if re.match(r'^\d{1,2}:\d{2}\s', input_text):
        subprocess.run(["sudo", "/usr/bin/systemd-run", "--on-calendar", f'{time}:00', send_message_command, message])
        result = "OK"
    # after X seconds, minutes or hours match
    elif re.match(r'^\d+[smh]\s', input_text):
        subprocess.run(["sudo", "/usr/bin/systemd-run", "--on-active", time, send_message_command, message])
        result = "OK"
    else:
        result = f"Parse error in time format\n" + help_message
    return result

def oblique():
    ob_st_file = '/data/repositories/telegram_bot/oblique_strategies/oblique_strategies_2015.json'
    try:
        with open(ob_st_file, 'r') as file:
            # Load the JSON data as a Python list
            data_list = json.load(file)

            if isinstance(data_list, list) and data_list: # Check if it's a non-empty list
                # Use random.choice() to pick one random dictionary from the list
                random_entry = random.choice(data_list)
                
                # Extract the value from the randomly selected dictionary
                if "card" in random_entry:
                    result = random_entry["card"]
                else:
                    result = "Error: The random entry did not have a 'card' key."
                    
            elif not data_list:
                result = "Error: The JSON list is empty."
            else:
                result = "Error: JSON file did not contain a list of objects."

    except json.JSONDecodeError:
        result = f"Error: Could not decode JSON from the file '{ob_st_file}'. Check file format."
    except Exception as e:
        result = f"An unexpected error occurred: {e}"

    return result 

if __name__ == "__main__":
    print(uptime())
    print(ip())
    print(fortune())
    audio_to_wav("/tmp/voice_file.ogg")
