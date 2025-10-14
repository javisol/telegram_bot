import re
import subprocess
import requests

def uptime():
    return(subprocess.check_output("uptime").decode('utf-8'))

def ip():
    return("IP: " + requests.get('https://ifconfig.me').text)

def geoip(input_text):
    ip = input_text[5:]
    result = subprocess.run([f"ssh reverse geoiplookup {ip}"], shell=True, capture_output=True, text=True)
    return result.stdout 

def fortune():
    result = subprocess.run(["fortune -a"], shell=True, capture_output=True, text=True)
    return result.stdout

def firewall_flush():
    result = subprocess.run(["ssh reverse sudo fwflush"], shell=True, capture_output=True, text=True)

def firewall_unban(input_text):
    jail_and_ip = input_text[7:] #remove /unban command form input_text
    result = subprocess.run([f"ssh reverse sudo unban {jail_and_ip}"], shell=True, capture_output=True, text=True)
    return result.stdout 

def firewall_fail2ban(input_text):
    start_stop = input_text[10:] #remove /unban command form input_text
    result = subprocess.run([f"ssh reverse sudo f2b {start_stop}"], shell=True, capture_output=True, text=True)
    return result.stdout 

def audio_to_wav(file_path):
    output_file = "/tmp/voice_file.wav"
    result = subprocess.run([f"ffmpeg -y -hide_banner -loglevel error -i {file_path} {output_file}"], shell=True, capture_output=True, text=True)
    return output_file

def audio_to_wav(file_path):
    output_file = "/tmp/voice_file.wav"
    result = subprocess.run([f"ffmpeg -y -hide_banner -loglevel error -i {file_path} {output_file}"], shell=True, capture_output=True, text=True)
    return output_file

def talk(input_text):
    #output_file = "/tmp/voice_file.ogg"
    #result = subprocess.run([f"espeak -s135 -ves --stdout \"{input_text}\" |oggenc -Q -o {output_file} -"], shell=True, capture_output=True, text=True)
    input_text = input_text[7:]
    result = subprocess.run([f"/usr/local/bin/assistant/ratoncio_send_voice \"{input_text}\""], shell=True, capture_output=True, text=True)

def reminder(input_text):
    send_message_command = "/usr/local/bin/assistant/ratoncio_send_msg"
    input_text = input_text[8:]
    time, message = input_text.split(None, 1)
    if re.match(r'^\d{1,2}:\d{2}\s', input_text):
        result = subprocess.run(["sudo", "/usr/bin/systemd-run", "--on-calendar", f'{time}:00', send_message_command, message])
    elif re.match(r'^\d+[smh]\s', input_text):
        result = subprocess.run(["sudo", "/usr/bin/systemd-run", "--on-active", time, send_message_command, message])
    else:
        result = "Parse error in time format"
    return result


if __name__ == "__main__":
    print(uptime())
    print(ip())
    print(fortune())
    audio_to_wav("/tmp/voice_file.ogg")