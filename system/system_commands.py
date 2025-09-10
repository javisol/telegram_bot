import subprocess
import requests

def uptime():
    return(subprocess.check_output("uptime").decode('utf-8'))

def ip():
    return("IP: " + requests.get('https://ifconfig.me').text)

def fortune():
    result = subprocess.run(["fortune -a"], shell=True, capture_output=True, text=True)
    return result.stdout

def firewall_flush():
    result = subprocess.run(["ssh reverse sudo fwflush"], shell=True, capture_output=True, text=True)
    return result.stdout

def firewall_unban():
    result = subprocess.run(["ssh reverse sudo unban"], shell=True, capture_output=True, text=True)
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


if __name__ == "__main__":
    print(uptime())
    print(ip())
    print(fortune())
    audio_to_wav("/tmp/voice_file.ogg")